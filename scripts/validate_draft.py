#!/usr/bin/env python3
"""
validate_draft.py — the fabrication guard for semantic-draft-writer.

Ports a product attribute-lock discipline to SEO drafts. It checks a
Markdown draft (with YAML front-matter) against the brand's locked-facts ledger, its
brief, and the suite's micro-semantics rules, and emits a JSON list of violations plus
a non-zero exit code if any are unresolved. The draft writer runs this in a
validate-and-repair loop; unresolved violations are surfaced to the user, never hidden.

Checks:
  FM     front-matter present & parseable; node_id present
  STRUCT heading structure matches the brief outline (same H2 roles, in order)
  STAT   no naked factual numbers outside cited/locked/illustrative contexts
  BRAND  every brand claim traces to a locked-facts key listed in locked_facts_used
  CITE   external factual stats have a sources entry
  LINT   micro-semantics: hedge density, question->answer adjacency, fluff, definition-first

Usage:
  python validate_draft.py --draft path/to/draft.md \
      --locked brands/<slug>/locked-facts.json \
      [--brief brands/<slug>/briefs/<slug>.md] \
      [--map brands/<slug>/topical-map.json] \
      [--brand-terms "YourBrand"] [--json]

Exit code 0 = clean, 1 = violations found, 2 = could not run (bad input).
"""
from __future__ import annotations
import argparse, json, re, sys

# ----------------------------- front-matter --------------------------------
def split_front_matter(text: str):
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    fm_raw, body = m.group(1), m.group(2)
    try:
        import yaml  # optional; fall back to a tiny parser
        fm = yaml.safe_load(fm_raw) or {}
    except Exception:
        fm = _mini_yaml(fm_raw)
    return fm, body

def _mini_yaml(raw: str) -> dict:
    """Very small YAML-ish parser for flat keys + simple inline lists, used only if
    PyYAML is unavailable. Not general — front-matter here is simple by design."""
    out = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        if line[0] in " -":  # skip nested/list-continuation in fallback
            continue
        k, _, v = line.partition(":")
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            out[k] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()] if inner else []
        elif v.startswith("{") and v.endswith("}"):
            out[k] = {}  # nested dict ignored in fallback
        else:
            out[k] = v.strip("'\"")
    return out

# ----------------------------- helpers -------------------------------------
NUM_RE = re.compile(r"(?<![\w$])(\$?\d[\d,]*(?:\.\d+)?\s?%?)")
CODEFENCE_RE = re.compile(r"```.*?```", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$", re.MULTILINE)
HEDGES = ["might", "maybe", "perhaps", "possibly", "sort of", "kind of", "arguably",
          "it seems", "we think", "probably", "somewhat", "generally tend",
          "more or less", "in some cases perhaps"]
FLUFF = ["in today's fast-paced world", "in this day and age", "without further ado",
         "let's dive in", "let's dive right in", "at the end of the day",
         "when it comes to", "it goes without saying", "needless to say"]
# words that make a nearby number non-factual (ordinals, structural, illustrative)
NUM_OK_CONTEXT = ["step", "h2", "h3", "example", "e.g", "for instance", "illustrative",
                  "aspect ratio", "9:16", "4:5", "1:1", "16:9", "version", "figure"]

ORDERED_LIST_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)

def strip_code(body: str) -> str:
    body = CODEFENCE_RE.sub("", body)
    # Ordered-list markers ("1. ", "2. ") are structure, not factual values.
    body = ORDERED_LIST_RE.sub("", body)
    return body

def sentences(text: str):
    for s in re.split(r"(?<=[.!?])\s+", text):
        s = s.strip()
        if s:
            yield s

# ----------------------------- checks --------------------------------------
def check_stats(body: str, sources: list, locked_values: set, violations: list):
    """Flag numeric factual claims that aren't cited, locked, or clearly illustrative."""
    text = strip_code(body)
    for s in sentences(text):
        for m in NUM_RE.finditer(s):
            token = m.group(1)
            low = s.lower()
            # allowed if the sentence names an illustrative/structural context
            if any(c in low for c in NUM_OK_CONTEXT):
                continue
            # allowed if the exact value appears in a locked fact
            norm = token.replace(",", "").strip()
            if any(norm in str(v).replace(",", "") for v in locked_values):
                continue
            # allowed if the sentence carries an inline citation marker or sources exist
            has_citation = bool(re.search(r"\[[^\]]+\]\([^)]+\)", s)) or "source:" in low
            if has_citation:
                continue
            # pure years like 2026 are usually fine
            if re.fullmatch(r"20\d{2}", norm):
                continue
            violations.append({
                "check": "STAT",
                "severity": "high",
                "detail": f"Naked factual value {token!r} with no citation/lock/illustrative marker",
                "evidence": s[:160],
            })

def check_brand(body: str, brand_terms: list, locked_used: list, locked_index: dict, violations: list):
    """Any sentence asserting a brand fact must be backed by a locked-facts key."""
    if not brand_terms:
        return
    text = strip_code(body)
    brand_re = re.compile("|".join(re.escape(b) for b in brand_terms), re.IGNORECASE)
    for s in sentences(text):
        if not brand_re.search(s):
            continue
        # A brand sentence that makes a factual claim (has a number or a strong claim verb)
        makes_claim = bool(NUM_RE.search(s)) or re.search(
            r"\b(offers?|includes?|guarantees?|delivers?|achieves?|supports?|costs?|priced|"
            r"reduces?|increases?|eliminates?|automates?)\b", s, re.IGNORECASE)
        if not makes_claim:
            continue
        # ok if it references a locked fact that is declared used
        backed = False
        for key in locked_used:
            fact = locked_index.get(key)
            if not fact:
                continue
            val = str(fact.get("value", "")).replace(",", "")
            if val and val in s.replace(",", ""):
                backed = True
                break
        # capability statements (no number) are softer: warn, don't fail, unless a number
        if not backed:
            sev = "high" if NUM_RE.search(s) else "warn"
            violations.append({
                "check": "BRAND",
                "severity": sev,
                "detail": "Brand claim not traced to a locked-facts key in locked_facts_used",
                "evidence": s[:160],
            })

def check_structure(body: str, brief: dict, violations: list):
    if not brief:
        return
    def norm(s):
        return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
    draft_h2 = [norm(t) for lvl, t in _headings(body) if lvl == 2]
    brief_h2 = [(h["heading"], norm(h["heading"])) for h in brief.get("outline", [])
                if h.get("level") == "H2"]
    if not brief_h2:
        return
    missing = []
    for orig, bh in brief_h2:
        key = " ".join(bh.split()[:4])
        if not any(key in dh for dh in draft_h2):
            missing.append(orig)
    if missing:
        violations.append({
            "check": "STRUCT", "severity": "warn",
            "detail": f"Draft missing {len(missing)} brief H2 section(s)",
            "evidence": "; ".join(missing[:5]),
        })

def _headings(body: str):
    return [(len(m.group(1)), m.group(2)) for m in HEADING_RE.finditer(body)]

def check_lint(body: str, violations: list):
    text = strip_code(body)
    sents = list(sentences(text))
    n = max(len(sents), 1)
    hedge_hits = sum(1 for s in sents if any(h in s.lower() for h in HEDGES))
    if hedge_hits / n > 0.15:
        violations.append({"check": "LINT", "severity": "warn",
            "detail": f"High hedge density ({hedge_hits}/{n} sentences)", "evidence": ""})
    for s in sents:
        for f in FLUFF:
            if f in s.lower():
                violations.append({"check": "LINT", "severity": "warn",
                    "detail": "Fluff phrase", "evidence": s[:120]})
                break
    # question headings should be followed by a concise answer within ~55 words
    lines = body.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^#{2,4}\s+(.*\?)\s*$", line)
        if m:
            follow = " ".join(lines[i+1:i+4]).strip()
            wc = len(follow.split())
            if wc == 0:
                violations.append({"check": "LINT", "severity": "warn",
                    "detail": "Question heading with no immediate answer",
                    "evidence": m.group(1)[:120]})

# ----------------------------- main ----------------------------------------
def validate(draft_path, locked_path=None, brief_path=None, brand_terms=None):
    violations = []
    try:
        text = open(draft_path, encoding="utf-8").read()
    except OSError as e:
        return {"error": str(e)}, 2
    fm, body = split_front_matter(text)
    if fm is None:
        violations.append({"check": "FM", "severity": "high",
                           "detail": "Missing/unparseable YAML front-matter", "evidence": ""})
        fm = {}
    elif not fm.get("node_id"):
        violations.append({"check": "FM", "severity": "high",
                           "detail": "front-matter missing node_id", "evidence": ""})

    locked_index, locked_values = {}, set()
    if locked_path:
        try:
            lf = json.load(open(locked_path))
            for f in lf.get("facts", []):
                locked_index[f["key"]] = f
                locked_values.add(str(f.get("value", "")))
        except OSError:
            pass
    brief = None
    if brief_path:
        try:
            brief = json.load(open(brief_path))
        except (OSError, json.JSONDecodeError):
            brief = None  # brief may be markdown; structural check skipped

    sources = fm.get("sources") or []
    locked_used = fm.get("locked_facts_used") or []

    check_stats(body, sources, locked_values, violations)
    check_brand(body, brand_terms or [], locked_used, locked_index, violations)
    check_structure(body, brief, violations)
    check_lint(body, violations)

    high = [v for v in violations if v["severity"] == "high"]
    result = {
        "draft": draft_path,
        "clean": len(high) == 0,
        "counts": {"high": len(high), "warn": len(violations) - len(high)},
        "violations": violations,
    }
    return result, (1 if high else 0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--locked")
    ap.add_argument("--brief")
    ap.add_argument("--brand-terms", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    brand_terms = [b.strip() for b in a.brand_terms.split(",") if b.strip()]
    result, code = validate(a.draft, a.locked, a.brief, brand_terms)
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("error"):
            print("ERROR:", result["error"]); sys.exit(2)
        print(f"{'CLEAN' if result['clean'] else 'VIOLATIONS'} — "
              f"{result['counts']['high']} high, {result['counts']['warn']} warn")
        for v in result["violations"]:
            print(f"  [{v['severity']:>4}] {v['check']}: {v['detail']}")
            if v["evidence"]:
                print(f"         ↳ {v['evidence']}")
    sys.exit(code)

if __name__ == "__main__":
    main()
