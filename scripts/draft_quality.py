#!/usr/bin/env python3
"""
draft_quality.py — editorial depth/quality scorer for semantic-draft-writer.

The suite already gates fabrication (validate_draft.py) and citation-readiness
(aeo_score.py). Nothing measured whether a draft is actually GOOD — deep, specific,
example-rich — so drafts drifted toward thin, formulaic FAQ prose that passed the other
two checks. This scores the missing dimension so the writer optimizes for merit, not just
for passing gates.

Every signal is mechanical and checkable — it flags genericness, it does not judge taste.

Signals (0-100):
  DEPTH       25  median words per H2 section (shallow sections = low)
  EXAMPLES    20  share of H2 sections with a concrete example/illustration
  SPECIFIC    20  density of concrete anchors: named entities, figures, citations
  ANTIFLUFF   20  low density of vague filler ("varies", "leverage", "robust", ...)
  LENGTH      15  total body length vs a floor (pillars should be substantial)

Advisory, like aeo_score. Exit 0 by default; --min N fails below a score.

Usage:
  python draft_quality.py --draft path/to/draft.md [--floor 800] [--json] [--min 70]
  python draft_quality.py --selftest
"""
from __future__ import annotations
import argparse, json, re, statistics, sys

FILLER = [
    "varies", "depends on", "a lot of", "a variety of", "a range of", "in general",
    "generally speaking", "when it comes to", "is key", "is important", "is crucial",
    "plays a role", "plays a vital role", "plays a critical role", "leverage", "utilize",
    "seamless", "robust", "cutting-edge", "state-of-the-art", "in today's", "the world of",
    "navigate the", "unlock", "supercharge", "game-changer", "game changer", "more than ever",
    "at the end of the day", "needless to say", "it's worth noting", "a myriad of",
    "take it to the next level", "best-in-class", "powerful tool", "wide range",
]
EXAMPLE_MARKERS = ["for example", "for instance", "e.g.", "such as", "imagine ",
                   "consider ", "say you", "case study", "in practice", "picture "]
STOP_CAPS = {"The", "A", "An", "This", "That", "These", "Those", "It", "They", "In",
             "For", "When", "Why", "How", "What", "Which", "Who", "Because", "If",
             "But", "And", "So", "Yes", "No", "Choose", "Match", "Pick", "Every",
             "Some", "Most", "More", "Both", "Each", "Beyond", "Modern", "Independent"}

def split_fm(text):
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n?(.*)$", text, re.DOTALL)
        if m:
            return m.group(1)
    return text

def strip_noise(t):
    t = re.sub(r"```.*?```", "", t, flags=re.DOTALL)      # code
    t = re.sub(r"^\s*\|.*\|\s*$", "", t, flags=re.M)       # table rows
    return t

def words(t):
    return len(re.findall(r"\w+", t))

def h2_sections(body):
    parts = re.split(r"^##\s+(.+)$", body, flags=re.M)
    out = []
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1] if i + 1 < len(parts) else ""))
    return out

def score(text, floor=800):
    body = strip_fm(text) if False else split_fm(text)
    clean = strip_noise(body)
    total_words = words(clean)
    secs = h2_sections(body)
    comp, fixes = {}, []

    # DEPTH — median words per H2 section
    sec_words = [words(strip_noise(b)) for _, b in secs] or [0]
    med = statistics.median(sec_words)
    comp["DEPTH"] = round(25 * min(1.0, med / 90.0))
    if med < 90:
        thin = [h for (h, b) in secs if words(strip_noise(b)) < 60]
        fixes.append(f"DEPTH: sections are shallow (median {med:.0f} words/H2). Go deeper: "
                     + (f"thin sections: {', '.join(thin[:3])}" if thin else "add mechanism, examples, trade-offs."))

    # EXAMPLES — share of sections with a concrete illustration
    with_ex = sum(1 for _, b in secs if any(m in b.lower() for m in EXAMPLE_MARKERS))
    frac = with_ex / len(secs) if secs else 0
    comp["EXAMPLES"] = round(20 * min(1.0, frac / 0.6))
    if frac < 0.6:
        fixes.append(f"EXAMPLES: only {with_ex}/{len(secs)} sections have a concrete example. "
                     "Add a specific 'for example…' or a named scenario per section.")

    # SPECIFIC — concrete anchors per 100 words: named entities + figures + citations
    caps = [w for w in re.findall(r"(?<![.!?]\s)\b[A-Z][a-zA-Z0-9.]{2,}\b", clean) if w not in STOP_CAPS]
    figures = re.findall(r"(?<![\w$])\$?\d[\d,]*(?:\.\d+)?%?", clean)
    cites = re.findall(r"\[[^\]]+\]\([^)]+\)", body)
    density = (len(caps) + len(figures) + len(cites)) / max(total_words, 1) * 100
    comp["SPECIFIC"] = round(20 * min(1.0, density / 3.0))
    if density < 3.0:
        fixes.append(f"SPECIFIC: low concrete-detail density ({density:.1f}/100w). Name real "
                     "tools/platforms/models, cite figures, reference specifics — not generic nouns.")

    # ANTIFLUFF — filler density (inverse)
    low = clean.lower()
    fill = sum(low.count(f) for f in FILLER)
    fill_density = fill / max(total_words, 1) * 100
    comp["ANTIFLUFF"] = round(20 * max(0.0, 1.0 - fill_density / 1.2))
    if fill_density > 0.4:
        hit = [f for f in FILLER if f in low][:5]
        fixes.append(f"ANTIFLUFF: filler density {fill_density:.1f}/100w. Cut/replace: {', '.join(hit)}.")

    # LENGTH — body vs floor
    comp["LENGTH"] = round(15 * min(1.0, total_words / floor))
    if total_words < floor:
        fixes.append(f"LENGTH: {total_words} words vs ~{floor} floor. Expand with depth, not padding.")

    tot = sum(comp.values())
    grade = ("excellent" if tot >= 85 else "good" if tot >= 70
             else "needs-work" if tot >= 50 else "thin")
    return {"score": tot, "grade": grade, "components": comp,
            "words": total_words, "sections": len(secs),
            "median_words_per_section": round(med), "fixes": fixes}

def selftest():
    good = """---
node_id: n-x
---
# Real title

Intro that names things concretely and sets up a specific argument about Kling and Meta.

## How does it actually work?
The pipeline renders a face with Nano Banana 2, then lip-syncs to the script frame by
frame. For example, a 15-second hook for a Shopify supplement brand needs the avatar to
hold the bottle at second 3; the model anchors that pose so it survives across shots.
In practice, teams re-run only the failed shot, not the whole ad, which is why a batch of
20 variants costs minutes rather than a shoot day. Consider a skincare brand testing five
hooks: each reuses the same locked creator, so the only variable is the script.

## Why does consistency beat realism?
Realism is table stakes now; consistency is the gap. When wardrobe or lighting drifts
between shots, viewers feel the seam even if each frame looks real. For instance, Arcads
clips are lifelike but can redraw a logo between cuts. Locking the creator and the set —
the way Seedance and continuity engines do — is what makes an ad read as one person, one
take, one story rather than a stitched montage.
"""
    bad = """---
node_id: n-y
---
# Some thoughts

## Overview
It varies a lot and depends on many factors. In general, when it comes to ads, quality is
key and you should leverage robust, cutting-edge tools to unlock a seamless workflow.

## More
There are a variety of options and it depends on your needs. At the end of the day, it is
important to utilize the right tool.
"""
    g, b = score(good, floor=250), score(bad, floor=250)
    assert g["score"] > b["score"], (g, b)
    assert g["score"] >= 70, g
    assert b["score"] < 50, b
    print(f"selftest ok — good={g['score']} ({g['grade']}) bad={b['score']} ({b['grade']})")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft"); ap.add_argument("--floor", type=int, default=800)
    ap.add_argument("--json", action="store_true"); ap.add_argument("--min", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not a.draft:
        print("error: --draft required", file=sys.stderr); sys.exit(2)
    try:
        r = score(open(a.draft, encoding="utf-8").read(), a.floor)
    except FileNotFoundError:
        print(f"error: no such draft {a.draft}", file=sys.stderr); sys.exit(2)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        c = r["components"]
        print(f"QUALITY {r['score']}/100 — {r['grade']}  "
              f"(DEPTH {c['DEPTH']} EXAMPLES {c['EXAMPLES']} SPECIFIC {c['SPECIFIC']} "
              f"ANTIFLUFF {c['ANTIFLUFF']} LENGTH {c['LENGTH']})")
        print(f"{r['words']} words · {r['sections']} sections · {r['median_words_per_section']} median words/section")
        for fx in r["fixes"]:
            print(f"  • {fx}")
    if a.min is not None and r["score"] < a.min:
        sys.exit(1)

if __name__ == "__main__":
    main()
