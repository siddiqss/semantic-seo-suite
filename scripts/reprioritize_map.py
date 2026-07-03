#!/usr/bin/env python3
"""
reprioritize_map.py — merge measured SERP data into a topical map and re-sort the content
calendar on REAL signals (T2). Turns the T0 qualitative order into a measured one and
flips each node's provenance from `asserted` to `measured`.

Provider-agnostic. Reads a signals file from EITHER:
  - dataforseo_client.py volume output   -> uses search_volume + competition
  - serpapi_client.py signals output     -> uses paa_count/related_count (demand breadth),
                                            organic_authority (difficulty), ads_count
Offline: it does not call any API, so it runs anywhere once the cache exists.

Priority score (derived, 0-100): business value (section+tier+intent) × demand ×
winnability. Signal-less nodes keep their qualitative rank, flagged.

Usage:
  python reprioritize_map.py --map brands/<slug>/topical-map.json \
      --signals brands/<slug>/data/serp/signals.json \
      --calendar brands/<slug>/calendar.md
  python reprioritize_map.py --selftest
"""
from __future__ import annotations
import argparse, json, math, re, sys

def norm(s): return re.sub(r"\s+", " ", (s or "").strip().lower())

def biz_weight(node):
    sect = {"core": 1.0, "outer": 0.6}.get(node.get("section"), 0.5)
    tier = {"pillar": 1.0, "cluster": 0.85, "supporting": 0.7}.get(node.get("tier"), 0.7)
    intent = {"commercial": 1.0, "informational": 0.8}.get(node.get("intent"), 0.8)
    return sect * tier * intent

def _log01(x, cap):
    """0..1 log-damped so a head term doesn't bury everything. None -> None."""
    if x is None:
        return None
    return min(1.0, math.log10(x + 1) / math.log10(cap + 1))

def metrics(row):
    """(demand, difficulty, commercial) each 0..1 or None, from either provider shape.
    DataForSEO: search_volume + competition. SerpApi: paa/related breadth + organic
    authority + ads. Nothing is estimated — absent signals stay None."""
    if not row:
        return None, None, None
    sv = row.get("search_volume")
    vol = sv.get("value") if isinstance(sv, dict) else row.get("volume")
    comp = row.get("competition")
    if vol is not None:                                    # DataForSEO
        diff = max(0.0, min(1.0, comp)) if isinstance(comp, (int, float)) else None
        commercial = 1.0 if isinstance(comp, (int, float)) and comp > 0.5 else 0.0
        return _log01(vol, 10000), diff, commercial
    if any(k in row for k in ("paa_count", "related_count", "organic_authority", "ads_count")):  # SerpApi
        breadth = (row.get("paa_count") or 0) + (row.get("related_count") or 0)
        oa = row.get("organic_authority")
        diff = min(1.0, oa / 8.0) if oa is not None else None   # up to 8/10 strong incumbents
        commercial = min(1.0, (row.get("ads_count") or 0) / 6.0)
        return _log01(breadth, 20), diff, commercial
    return None, None, None

def winnability(difficulty):
    if difficulty is None:
        return 0.6                                          # neutral floor when unknown
    return 1.0 - 0.7 * max(0.0, min(1.0, difficulty))

def score(node, demand, difficulty, commercial=0.0):
    d = 0.5 if demand is None else demand
    base = biz_weight(node) * d * winnability(difficulty)
    if node.get("intent") == "commercial":
        base *= 1.0 + 0.15 * (commercial or 0.0)            # SERP shows commercial pull
    return round(100 * base, 1)

def load_signals(path):
    """Accept a client output list (DataForSEO volume or SerpApi signals) -> {kw: row}."""
    data = json.load(open(path))
    rows = data if isinstance(data, list) else data.get("results", [])
    return {norm(r.get("keyword")): r for r in rows if isinstance(r, dict) and r.get("keyword")}

def merge(map_obj, sig):
    hits = 0
    for n in map_obj["nodes"]:
        row = sig.get(norm(n.get("target_query")))
        demand, diff, commercial = metrics(row)
        if demand is not None or diff is not None:
            hits += 1
            n["intent_provenance"] = "measured"
            if row.get("search_volume") or row.get("volume") is not None:
                v = row["search_volume"]["value"] if isinstance(row.get("search_volume"), dict) else row.get("volume")
                n["volume"] = {"value": v, "provenance": "measured", "source": row.get("source", "dataforseo")}
            n["signals"] = {"demand": None if demand is None else round(demand, 3),
                            "difficulty": None if diff is None else round(diff, 3),
                            "commercial": round(commercial or 0.0, 3),
                            "raw": {k: row[k] for k in
                                    ("paa_count", "related_count", "organic_authority", "ads_count", "competition")
                                    if k in row},
                            "provenance": "measured", "source": row.get("source", "serp")}
            n["priority_score"] = {"value": score(n, demand, diff, commercial),
                                   "provenance": "derived", "source": "reprioritize_map:biz×demand×winnability"}
        else:
            n["priority_score"] = {"value": round(100 * biz_weight(n) * 0.5 * 0.6, 1),
                                   "provenance": "derived", "note": "no SERP signal — qualitative fallback"}
    return hits

def resort_calendar(map_obj, cal_path, per_week=3):
    nodes = sorted(map_obj["nodes"], key=lambda n: n["priority_score"]["value"], reverse=True)
    lines = ["# Content Calendar — re-prioritized on measured SERP signals",
             f"Cadence: {per_week}/week · Order = measured priority "
             "(business value × demand × winnability). `~` = no SERP signal, qualitative rank.",
             "", "| # | Node | Tier | Section | Intent | Demand | Diff | Priority | Week |",
             "|---|---|---|---|---|---|---|---|---|"]
    for i, n in enumerate(nodes):
        wk = f"W{i // per_week + 1}"
        sg = n.get("signals") or {}
        dem = f"{int(sg['demand']*100)}" if sg.get("demand") is not None else "~"
        dff = f"{int(sg['difficulty']*100)}" if sg.get("difficulty") is not None else "~"
        lines.append(f"| {i+1} | {n['title']} | {n['tier']} | {n['section']} | {n['intent']} | "
                     f"{dem} | {dff} | {n['priority_score']['value']} | {wk} |")
    open(cal_path, "w").write("\n".join(lines) + "\n")
    return nodes[0]["title"], nodes[0]["priority_score"]["value"]

def selftest():
    m = {"nodes": [
        {"id": "a", "title": "commercial head", "section": "core", "tier": "pillar",
         "intent": "commercial", "target_query": "best ai ugc ad tools"},
        {"id": "b", "title": "tiny outer term", "section": "outer", "tier": "supporting",
         "intent": "informational", "target_query": "ad metrics roas"},
        {"id": "c", "title": "no data node", "section": "core", "tier": "cluster",
         "intent": "commercial", "target_query": "obscure long tail"},
    ]}
    # SerpApi-shaped signals: strong SERP for the head term, thin for the outer term
    sig = {"best ai ugc ad tools": {"keyword": "best ai ugc ad tools", "paa_count": 4,
                                    "related_count": 8, "organic_authority": 3, "ads_count": 4,
                                    "source": "serpapi:google_serp"},
           "ad metrics roas": {"keyword": "ad metrics roas", "paa_count": 1,
                               "related_count": 1, "organic_authority": 1, "ads_count": 0,
                               "source": "serpapi:google_serp"}}
    hits = merge(m, sig)
    assert hits == 2, hits
    s = {n["id"]: n["priority_score"]["value"] for n in m["nodes"]}
    assert s["a"] > s["b"], s                               # commercial core beats tiny outer
    assert m["nodes"][0]["signals"]["provenance"] == "measured"
    assert "note" in m["nodes"][2]["priority_score"]        # signal-less node flagged
    # winnability: high incumbent authority lowers score at equal demand
    hi = score({"section": "core", "tier": "pillar", "intent": "commercial"}, 0.8, 0.9)
    lo = score({"section": "core", "tier": "pillar", "intent": "commercial"}, 0.8, 0.1)
    assert lo > hi, (lo, hi)
    # DataForSEO shape still works (backward compatible)
    d, df, _ = metrics({"search_volume": {"value": 8000}, "competition": 0.3})
    assert d and df == 0.3
    print(f"selftest ok — SerpApi+DataForSEO both parse; a({s['a']}) > b({s['b']}); winnability holds")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map"); ap.add_argument("--signals"); ap.add_argument("--calendar")
    ap.add_argument("--volumes", help="alias for --signals (back-compat)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    sig_path = a.signals or a.volumes
    if not (a.map and sig_path and a.calendar):
        print("error: --map, --signals, --calendar required", file=sys.stderr); sys.exit(2)
    map_obj = json.load(open(a.map))
    hits = merge(map_obj, load_signals(sig_path))
    json.dump(map_obj, open(a.map, "w"), indent=2); open(a.map, "a").write("\n")
    top, top_score = resort_calendar(map_obj, a.calendar)
    print(json.dumps({"nodes": len(map_obj["nodes"]), "with_signal": hits,
                      "top_node": top, "top_score": top_score}, indent=2))

if __name__ == "__main__":
    main()
