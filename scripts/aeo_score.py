#!/usr/bin/env python3
"""
aeo_score.py — citation-readiness scorer for answer-engine-optimizer.

Answer engines (Google AI Overviews, ChatGPT, Perplexity, Gemini) lift *extractable,
self-contained* passages. This scores a Markdown draft on the structural signals that
make a passage liftable — the same discipline validate_draft.py applies to fabrication,
turned toward citability. Every signal is mechanically checkable; nothing is estimated.

It is ADVISORY, not a gate: exit 0 by default. Pass --min N to fail (exit 1) below a
score, e.g. in a pre-publish check.

Signals (0-100):
  DEF   definition-first lead        15   first paragraph defines the subject, <=50 words
  QA    question-H2 answer coverage  30   question headings answered in <=50 words right after
  TLDR  extractive summary up top    10   a short standalone summary in the first blocks
  LIFT  structured blocks            15   >=1 list and/or table (engines quote these)
  BREV  answer-sentence brevity      10   median answer sentence <=25 words
  SELF  self-contained claims        10   paragraphs don't open with a dangling This/It/That
  SCHEMA machine context             10   front-matter schema_type present (or --schema-dir hit)

Usage:
  python aeo_score.py --draft path/to/draft.md [--schema-dir brands/<slug>/data/schema] [--json] [--min 70]
  python aeo_score.py --selftest      # runnable check: good draft must outscore bad

Exit: 0 ok (or advisory), 1 below --min, 2 could not run.
"""
from __future__ import annotations
import argparse, json, os, re, sys, statistics

Q_STARTS = ("what", "why", "how", "when", "where", "which", "who",
            "is", "are", "can", "do", "does", "should", "will", "vs")
DANGLING = ("this ", "that ", "it ", "these ", "those ", "they ")

def split_front_matter(text: str):
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    fm = {}
    for line in raw.splitlines():
        if ":" in line and not line[:1] in " -":
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, body

def blocks(body: str):
    """Split into (kind, text) blocks. kind in {h1,h2,h3,list,table,para}."""
    out, buf = [], []
    def flush():
        if buf:
            out.append(("para", " ".join(buf).strip()))
            buf.clear()
    for line in body.splitlines():
        s = line.strip()
        if not s:
            flush(); continue
        if s.startswith("#"):
            flush()
            lvl = len(s) - len(s.lstrip("#"))
            out.append((f"h{min(lvl,3)}", s.lstrip("# ").strip()))
        elif re.match(r"^([-*]|\d+\.)\s", s):
            flush(); out.append(("list", s))
        elif s.startswith("|"):
            flush(); out.append(("table", s))
        else:
            buf.append(s)
    flush()
    return out

def words(t): return len(re.findall(r"\w+", t))
def sentences(t): return [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s]
def is_question(h): return h.lower().rstrip("?:").split()[:1] and (
    h.lower().split()[0] in Q_STARTS or h.rstrip().endswith("?"))

def score(text: str, schema_hit: bool):
    fm, body = split_front_matter(text)
    bl = blocks(body)
    findings, comp = [], {}

    # DEF — first paragraph after the H1 defines the subject in <=50 words
    lead = next((t for k, t in bl if k == "para"), "")
    def_ok = lead and words(lead) <= 55 and re.search(r"\b(is|are|means|refers to)\b", lead.lower())
    comp["DEF"] = 15 if def_ok else 0
    if not def_ok:
        findings.append("DEF: lead paragraph should define the subject in one <=50-word declarative sentence.")

    # QA — question H2s answered tightly right after
    answer_paras = []
    q_total = q_answered = 0
    for i, (k, t) in enumerate(bl):
        if k == "h2" and is_question(t):
            q_total += 1
            nxt = bl[i + 1] if i + 1 < len(bl) else ("", "")
            if nxt[0] == "para" and words(nxt[1]) <= 50:
                q_answered += 1
                answer_paras.append(nxt[1])
            else:
                findings.append(f"QA: '{t}' — follow it immediately with a <=50-word answer, then elaborate.")
    comp["QA"] = round(30 * (q_answered / q_total)) if q_total else 15
    if q_total == 0:
        findings.append("QA: no question-style H2s — engines match Q&A shapes; phrase key headings as questions.")

    # TLDR — a short standalone summary in the first 3 blocks (or front-matter snippet)
    top = [t for k, t in bl[:4] if k == "para"]
    tldr_ok = bool(fm.get("snippet_target")) or any(words(t) <= 60 for t in top)
    comp["TLDR"] = 10 if tldr_ok else 0
    if not tldr_ok:
        findings.append("TLDR: add a <=60-word extractive summary near the top (or a snippet_target in front-matter).")

    # LIFT — lists and tables get quoted verbatim
    has_list = any(k == "list" for k, _ in bl)
    has_table = any(k == "table" for k, _ in bl)
    comp["LIFT"] = (8 if has_list else 0) + (7 if has_table else 0)
    if not has_list and not has_table:
        findings.append("LIFT: add at least one list or comparison table — engines lift structured blocks directly.")

    # BREV — median answer sentence <=25 words
    lens = [words(s) for p in answer_paras for s in sentences(p)]
    if lens:
        med = statistics.median(lens)
        comp["BREV"] = 10 if med <= 25 else (5 if med <= 32 else 0)
        if med > 25:
            findings.append(f"BREV: answer sentences run long (median {med:.0f} words) — tighten to <=25.")
    else:
        comp["BREV"] = 5  # neutral when there are no answer blocks yet

    # SELF — paragraphs shouldn't open with a dangling pronoun (breaks standalone extraction)
    paras = [t for k, t in bl if k == "para"]
    dangle = sum(1 for p in paras if p.lower().startswith(DANGLING))
    frac_ok = 1 - (dangle / len(paras)) if paras else 1
    comp["SELF"] = round(10 * frac_ok)
    if dangle:
        findings.append(f"SELF: {dangle} paragraph(s) open with a dangling 'This/It/That' — name the subject so the passage stands alone.")

    # SCHEMA
    comp["SCHEMA"] = 10 if (fm.get("schema_type") or schema_hit) else 0
    if comp["SCHEMA"] == 0:
        findings.append("SCHEMA: no schema_type in front-matter and no matching JSON-LD — add structured data for machine context.")

    total = sum(comp.values())
    grade = ("excellent" if total >= 85 else "good" if total >= 70
             else "needs-work" if total >= 50 else "poor")
    return {"score": total, "grade": grade, "components": comp,
            "questions": {"total": q_total, "answered": q_answered}, "fixes": findings}

def run(path, schema_dir):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    schema_hit = False
    fm, _ = split_front_matter(text)
    nid = fm.get("node_id")
    if schema_dir and nid and os.path.isdir(schema_dir):
        schema_hit = os.path.exists(os.path.join(schema_dir, f"{nid}.jsonld"))
    return score(text, schema_hit)

def selftest():
    good = ("---\nnode_id: n-x\nschema_type: Article\nsnippet_target: A UGC ad is a video that looks user-made.\n---\n"
            "# What is a UGC ad?\n\nA UGC ad is a video ad styled to look like an ordinary customer made it. "
            "It trades polish for authenticity.\n\n## Why do UGC ads convert?\n\nThey convert because they read as "
            "a peer recommendation, not a brand message, which lowers viewer resistance.\n\n"
            "- Feels authentic\n- Cheap to test\n\n| Type | Cost |\n|---|---|\n| AI | low |\n")
    bad = ("# Some thoughts on advertising\n\nThis is something we have been thinking about for a very long time and "
           "there are many considerations that go into the broad and sprawling topic of how modern brands might "
           "approach the ever-changing landscape of paid media over time.\n\n"
           "It depends on a lot of factors that we will explore below in great and winding detail.\n")
    g = score(good, schema_hit=False)
    b = score(bad, schema_hit=False)
    assert g["score"] > b["score"], (g, b)
    assert g["score"] >= 70, g
    assert b["score"] < 50, b
    print(f"selftest ok — good={g['score']} bad={b['score']}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft")
    ap.add_argument("--schema-dir")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not a.draft:
        print("error: --draft required", file=sys.stderr); sys.exit(2)
    try:
        r = run(a.draft, a.schema_dir)
    except FileNotFoundError:
        print(f"error: no such draft {a.draft}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        c = r["components"]
        print(f"AEO {r['score']}/100 — {r['grade']}  "
              f"(DEF {c['DEF']} QA {c['QA']} TLDR {c['TLDR']} LIFT {c['LIFT']} "
              f"BREV {c['BREV']} SELF {c['SELF']} SCHEMA {c['SCHEMA']})")
        print(f"question H2s answered: {r['questions']['answered']}/{r['questions']['total']}")
        for fx in r["fixes"]:
            print(f"  • {fx}")
    if a.min is not None and r["score"] < a.min:
        sys.exit(1)

if __name__ == "__main__":
    main()
