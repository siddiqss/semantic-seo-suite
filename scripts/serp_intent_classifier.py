#!/usr/bin/env python3
"""
serp_intent_classifier.py — classify search intent from the COMPOSITION of a SERP
(result types), upgrading a node's intent from `asserted` to `measured`. Works from a
SERP JSON you supply (from dataforseo_client.py live SERP, or a hand-built fixture);
does not itself scrape Google.

Heuristics (transparent, tunable):
  many shopping/product/ads + product-page results -> transactional
  many "best/review/comparison" listicles + PAA "vs"  -> commercial
  featured snippet / definitional / how-to / PAA questions -> informational
  brand-dominated single-site results -> navigational

Usage:
  python serp_intent_classifier.py --serp serp.json
  # serp.json: {"query":..., "results":[{"type":"organic","title":...,"url":...}, {"type":"shopping"...}, ...],
  #             "features":["featured_snippet","people_also_ask","shopping"]}
"""
from __future__ import annotations
import argparse, json, re

COMMERCIAL_RE = re.compile(r"\b(best|top \d+|review|reviews|vs|compare|comparison|alternative)\b", re.I)
TRANSACTIONAL_RE = re.compile(r"\b(buy|price|pricing|deal|shop|order|cheap|for sale|coupon)\b", re.I)
INFORMATIONAL_RE = re.compile(r"\b(what|why|how|guide|tutorial|meaning|definition|explained)\b", re.I)

def classify(serp):
    results = serp.get("results", [])
    features = set(serp.get("features", []))
    q = serp.get("query", "")
    score = {"informational": 0, "commercial": 0, "transactional": 0, "navigational": 0}

    if "shopping" in features: score["transactional"] += 3
    if "featured_snippet" in features: score["informational"] += 2
    if "people_also_ask" in features: score["informational"] += 1

    titles = " ".join(r.get("title", "") for r in results)
    types = [r.get("type", "organic") for r in results]
    score["transactional"] += 2 * sum(1 for t in types if t in ("shopping", "product", "ads"))
    score["commercial"] += len(COMMERCIAL_RE.findall(titles))
    score["transactional"] += len(TRANSACTIONAL_RE.findall(titles))
    score["informational"] += len(INFORMATIONAL_RE.findall(titles))
    # brand-dominated -> navigational
    domains = [re.sub(r"^https?://(www\.)?", "", r.get("url", "")).split("/")[0] for r in results if r.get("url")]
    if domains and len(set(domains)) <= max(1, len(domains) // 3):
        score["navigational"] += 2

    intent = max(score, key=score.get) if any(score.values()) else "informational"
    return {"query": q, "intent": intent, "scores": score,
            "provenance": "measured", "source": "serp_composition"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serp", required=True)
    a = ap.parse_args()
    print(json.dumps(classify(json.load(open(a.serp))), indent=2))

if __name__ == "__main__":
    main()
