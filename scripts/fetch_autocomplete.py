#!/usr/bin/env python3
"""
fetch_autocomplete.py — harvest real query variants from Google Autocomplete (Suggest).
Recursive expansion with a-z suffixes and question prefixes. Unofficial endpoint; may
change or rate-limit — wrap failures, never block the workflow.

Live network required.

Usage:
  python fetch_autocomplete.py --seed "sour espresso" [--depth 1] [--lang en] [--country US]
Output: {"seed":..., "suggestions":[{"query":...,"provenance":"measured","source":"google_autocomplete"}]}
"""
from __future__ import annotations
import argparse, json, sys, time, urllib.parse, urllib.request, string

UA = "Mozilla/5.0 SemanticSEOSuite/0.1"
ENDPOINT = "https://suggestqueries.google.com/complete/search"
QUESTION_PREFIXES = ["how", "what", "why", "best", "vs", "is", "can", "when"]

def suggest(q, lang, country):
    params = urllib.parse.urlencode({"client": "firefox", "q": q, "hl": lang, "gl": country})
    req = urllib.request.Request(f"{ENDPOINT}?{params}", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
        return data[1] if len(data) > 1 else []
    except Exception as e:
        sys.stderr.write(f"[autocomplete] '{q}' failed: {e}\n"); return []

def harvest(seed, depth, lang, country):
    out, seen = [], set()
    def add(items):
        for it in items:
            if it not in seen:
                seen.add(it); out.append(it)
    add(suggest(seed, lang, country))
    if depth >= 1:
        for suf in list(string.ascii_lowercase):
            add(suggest(f"{seed} {suf}", lang, country)); time.sleep(0.15)
        for pre in QUESTION_PREFIXES:
            add(suggest(f"{pre} {seed}", lang, country)); time.sleep(0.15)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--lang", default="en"); ap.add_argument("--country", default="US")
    a = ap.parse_args()
    items = harvest(a.seed, a.depth, a.lang, a.country)
    print(json.dumps({"seed": a.seed, "count": len(items),
        "suggestions": [{"query": q, "provenance": "measured", "source": "google_autocomplete"} for q in items]},
        indent=2))

if __name__ == "__main__":
    main()
