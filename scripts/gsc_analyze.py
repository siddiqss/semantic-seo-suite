#!/usr/bin/env python3
"""
gsc_analyze.py — turn a Search Console query+page pull into map-aware insights.

This is the JOIN/rollup layer on top of gsc_client.py output. It produces the *measured*
version of what SemanticOS fakes as "Pillar Page Rank", plus striking-distance
opportunities, decaying pages (with a prior period), measured cannibalization, and GSC
queries the map doesn't cover (feed back to topical-map-builder).

Everything here is `measured` (from GSC) or `derived` (rollups) — no invented metrics.

Usage:
  python gsc_analyze.py --gsc data/gsc/pull.json --map topical-map.json \
     [--gsc-prev data/gsc/prev.json] --out audits/<date>-performance.md
"""
from __future__ import annotations
import argparse, json, os, re
from collections import defaultdict


def norm_url(u):
    return re.sub(r"^https?://(www\.)?", "", (u or "").rstrip("/")).lower()


def match_page_to_node(url, nodes):
    nu = norm_url(url)
    for n in nodes:
        if n.get("url") and norm_url(n["url"]) == nu:
            return n["id"]
    # fuzzy: last path segment vs node id / slug words
    seg = nu.split("/")[-1]
    for n in nodes:
        if n["id"] in nu:
            return n["id"]
        words = set(re.sub(r"[^a-z0-9 ]", " ", n["title"].lower()).split())
        segwords = set(seg.replace("-", " ").split())
        if words and len(words & segwords) >= max(2, len(segwords) // 2):
            return n["id"]
    return None


def pillar_of(node_id, by_id):
    cur = by_id.get(node_id)
    seen = set()
    while cur and cur.get("parent") and cur["id"] not in seen:
        seen.add(cur["id"])
        cur = by_id.get(cur["parent"])
    return cur["id"] if cur else node_id


def rollup(rows, nodes):
    by_id = {n["id"]: n for n in nodes}
    pillar_agg = defaultdict(lambda: {"clicks": 0.0, "impressions": 0.0, "positions": [], "pages": set()})
    query_pages = defaultdict(set)     # query -> set(page)
    covered_queries = set()
    for n in nodes:
        for q in n.get("query_network", []):
            covered_queries.add(q["query"].lower())
        covered_queries.add(n.get("target_query", "").lower())

    striking, uncovered = [], defaultdict(lambda: {"impressions": 0.0, "clicks": 0.0})
    for r in rows:
        page = r.get("page"); q = r.get("query", "")
        nid = match_page_to_node(page, nodes) if page else None
        if page and q:
            query_pages[q.lower()].add(norm_url(page))
        if nid:
            pid = pillar_of(nid, by_id)
            pa = pillar_agg[pid]
            pa["clicks"] += r.get("clicks", 0) or 0
            pa["impressions"] += r.get("impressions", 0) or 0
            if r.get("position") is not None:
                pa["positions"].append(r["position"])
            if page: pa["pages"].add(norm_url(page))
        pos = r.get("position")
        if pos is not None and 5 <= pos <= 15:
            striking.append({"query": q, "page": norm_url(page) if page else None,
                             "position": round(pos, 1), "impressions": r.get("impressions"),
                             "provenance": "measured"})
        if q and q.lower() not in covered_queries:
            uncovered[q.lower()]["impressions"] += r.get("impressions", 0) or 0
            uncovered[q.lower()]["clicks"] += r.get("clicks", 0) or 0

    pillars = []
    for pid, pa in pillar_agg.items():
        avg_pos = round(sum(pa["positions"]) / len(pa["positions"]), 1) if pa["positions"] else None
        pillars.append({"pillar": pid, "title": by_id[pid]["title"],
                        "clicks": round(pa["clicks"]), "impressions": round(pa["impressions"]),
                        "avg_position": avg_pos, "pages": len(pa["pages"]),
                        "provenance": "derived"})
    pillars.sort(key=lambda x: -x["impressions"])

    cannibal = [{"query": q, "pages": sorted(ps), "provenance": "measured"}
                for q, ps in query_pages.items() if len(ps) > 1]
    striking.sort(key=lambda x: -(x["impressions"] or 0))
    new_nodes = sorted(({"query": q, **v, "provenance": "measured"} for q, v in uncovered.items()),
                       key=lambda x: -x["impressions"])[:25]
    return pillars, striking[:25], cannibal, new_nodes


def decay(rows, prev_rows, nodes):
    """Pages losing clicks vs a prior period."""
    def by_page(rs):
        agg = defaultdict(float)
        for r in rs:
            if r.get("page"):
                agg[norm_url(r["page"])] += r.get("clicks", 0) or 0
        return agg
    cur, prev = by_page(rows), by_page(prev_rows)
    out = []
    for p, c in prev.items():
        now = cur.get(p, 0.0)
        if c >= 5 and now < c * 0.7:  # lost >30% clicks
            out.append({"page": p, "prev_clicks": round(c), "clicks": round(now),
                        "change_pct": round((now - c) / c * 100, 1), "provenance": "measured"})
    out.sort(key=lambda x: x["change_pct"])
    return out


def to_md(pillars, striking, cannibal, new_nodes, decaying, brand):
    def T(rows, cols, hdr):
        head = "| " + " | ".join(hdr) + " |\n|" + "|".join(["---"] * len(hdr)) + "|"
        body = "\n".join("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows) or "| _none_ |" + " |" * (len(hdr) - 1)
        return head + "\n" + body
    md = [f"# Performance report (GSC) — {brand or 'site'}",
          "> All figures `measured` from Search Console; pillar rollups `derived`. No estimates.", ""]
    md += ["## Pillar performance (real 'Pillar Page Rank')",
           T(pillars, ["pillar", "title", "impressions", "clicks", "avg_position", "pages"],
             ["Pillar", "Title", "Impr", "Clicks", "Avg pos", "Pages"]), ""]
    md += ["## Striking-distance opportunities (position 5–15)",
           T(striking, ["query", "page", "position", "impressions"],
             ["Query", "Page", "Pos", "Impr"]), ""]
    md += ["## Measured cannibalization (one query → multiple pages)",
           T([{"query": c["query"], "pages": ", ".join(c["pages"])} for c in cannibal],
             ["query", "pages"], ["Query", "Pages"]), ""]
    md += ["## Decaying pages (vs prior period)",
           T(decaying, ["page", "prev_clicks", "clicks", "change_pct"],
             ["Page", "Prev clicks", "Clicks", "Change %"]), ""]
    md += ["## Uncovered queries → candidate new map nodes",
           T(new_nodes, ["query", "impressions", "clicks"], ["Query", "Impr", "Clicks"]), ""]
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gsc", required=True)
    ap.add_argument("--gsc-prev")
    ap.add_argument("--map", required=True)
    ap.add_argument("--brand", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gsc = json.load(open(a.gsc)); rows = gsc["rows"]
    nodes = json.load(open(a.map))["nodes"]
    pillars, striking, cannibal, new_nodes = rollup(rows, nodes)
    decaying = decay(rows, json.load(open(a.gsc_prev))["rows"], nodes) if a.gsc_prev else []
    open(a.out, "w").write(to_md(pillars, striking, cannibal, new_nodes, decaying, a.brand))
    json.dump({"pillars": pillars, "striking": striking, "cannibalization": cannibal,
               "new_node_candidates": new_nodes, "decaying": decaying},
              open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print(json.dumps({"out": a.out, "pillars": len(pillars), "striking": len(striking),
                      "cannibalization": len(cannibal), "new_candidates": len(new_nodes),
                      "decaying": len(decaying)}, indent=2))


if __name__ == "__main__":
    main()
