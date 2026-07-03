#!/usr/bin/env python3
"""
fetch_trends.py — relative interest + related queries via pytrends (unofficial Google
Trends). Fragile upstream; all failures wrapped. Returns RELATIVE demand only (not
absolute volume) — label accordingly.

Requires: pip install pytrends ; live network.

Usage:
  python fetch_trends.py --terms "sour espresso,bitter espresso" [--geo US] [--timeframe "today 12-m"]
"""
from __future__ import annotations
import argparse, json, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True)
    ap.add_argument("--geo", default="US"); ap.add_argument("--timeframe", default="today 12-m")
    a = ap.parse_args()
    terms = [t.strip() for t in a.terms.split(",") if t.strip()][:5]
    try:
        from pytrends.request import TrendReq
        py = TrendReq(hl="en-US", tz=0)
        py.build_payload(terms, geo=a.geo, timeframe=a.timeframe)
        iot = py.interest_over_time()
        avg = {t: (float(iot[t].mean()) if t in iot else None) for t in terms}
        related = {}
        try:
            rq = py.related_queries()
            for t in terms:
                top = rq.get(t, {}).get("top")
                related[t] = top.to_dict("records") if top is not None else []
        except Exception:
            related = {t: [] for t in terms}
        print(json.dumps({"geo": a.geo, "timeframe": a.timeframe,
            "relative_interest": {"value": avg, "provenance": "measured",
                                   "source": "google_trends", "note": "relative 0-100, not absolute volume"},
            "related_queries": related}, indent=2))
    except Exception as e:
        sys.stderr.write(f"[trends] unavailable: {e}\n")
        print(json.dumps({"error": str(e), "relative_interest": None}))

if __name__ == "__main__":
    main()
