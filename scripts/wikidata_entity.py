#!/usr/bin/env python3
"""
wikidata_entity.py — resolve an entity against Wikidata and return canonical typing +
key attributes (claims). Free, `measured` entity grounding for seo-brand-foundation
and topical-map-builder.

Live network required (www.wikidata.org).

Usage:
  python wikidata_entity.py --query "espresso machine" [--lang en]
Output: best-match QID, label, description, instance-of/subclass-of, and a sample of
property claims (attributes).
"""
from __future__ import annotations
import argparse, json, sys, urllib.parse, urllib.request

API = "https://www.wikidata.org/w/api.php"
UA = "SemanticSEOSuite/0.1"

def _get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))

def resolve(query, lang):
    s = _get({"action": "wbsearchentities", "search": query, "language": lang,
              "format": "json", "limit": 3})
    hits = s.get("search", [])
    if not hits:
        return None
    top = hits[0]
    ent = _get({"action": "wbgetentities", "ids": top["id"], "languages": lang,
                "format": "json", "props": "labels|descriptions|claims"})
    e = ent["entities"][top["id"]]
    claims = e.get("claims", {})
    # a few interpretable properties: P31 instance-of, P279 subclass-of
    def label_of(qid):
        try:
            r = _get({"action": "wbgetentities", "ids": qid, "languages": lang,
                      "format": "json", "props": "labels"})
            return r["entities"][qid]["labels"].get(lang, {}).get("value", qid)
        except Exception:
            return qid
    def prop_values(pid):
        vals = []
        for c in claims.get(pid, [])[:5]:
            try:
                dv = c["mainsnak"]["datavalue"]["value"]
                if isinstance(dv, dict) and "id" in dv:
                    vals.append(label_of(dv["id"]))
                else:
                    vals.append(dv)
            except Exception:
                pass
        return vals
    return {
        "qid": top["id"],
        "label": e.get("labels", {}).get(lang, {}).get("value", query),
        "description": e.get("descriptions", {}).get(lang, {}).get("value", ""),
        "instance_of": prop_values("P31"),
        "subclass_of": prop_values("P279"),
        "attribute_properties": list(claims.keys())[:30],
        "candidates": [{"id": h["id"], "label": h.get("label"), "desc": h.get("description")} for h in hits],
        "provenance": "measured", "source": f"wikidata:{top['id']}",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True); ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    try:
        res = resolve(a.query, a.lang)
        print(json.dumps(res or {"error": "no match", "query": a.query}, indent=2, ensure_ascii=False))
    except Exception as e:
        sys.stderr.write(f"[wikidata] failed: {e}\n")
        print(json.dumps({"error": str(e), "query": a.query}))

if __name__ == "__main__":
    main()
