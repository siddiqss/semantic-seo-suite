#!/usr/bin/env python3
"""
linking_plan.py — derive an internal-linking plan from a topical map (+ optional
embeddings for lateral-link justification and crawl data for orphan detection).

Implements internal-linking-rules.md: hub-and-spoke up/down links, justified laterals,
varied descriptive anchors drawn from the target node's query network, and orphan /
over-linked-hub detection.

Usage:
  python linking_plan.py --map brands/<slug>/topical-map.json \
      [--vecs vecs.npz --lateral-threshold 0.72] \
      [--crawl-dir brands/<slug>/data/crawl] --out linking-plan.md
"""
from __future__ import annotations
import argparse, json, os, sys, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def anchors_for(node, k=3):
    """Varied, descriptive anchors from the target node's query network (no exact-match
    spam). Falls back to the title."""
    qs = [q["query"] for q in node.get("query_network", [])]
    cands = []
    for q in qs:
        a = q.strip()
        if 2 <= len(a.split()) <= 7:
            cands.append(a)
    seen, out = set(), []
    for a in [node["title"]] + cands:
        key = a.lower()
        if key not in seen:
            seen.add(key); out.append(a)
        if len(out) >= k:
            break
    return out


def build(map_obj, vecs_path=None, lateral_threshold=0.72, crawl_dir=None):
    nodes = {n["id"]: n for n in map_obj["nodes"]}
    order = [n["id"] for n in map_obj["nodes"]]

    # embeddings (optional) for lateral justification
    sim = None
    if vecs_path and os.path.exists(vecs_path):
        from semantic_distance import load_vecs, cosine
        ids, vs, _ = load_vecs(vecs_path)
        idx = {i: k for k, i in enumerate(ids)}
        def sim(a, b):
            if a in idx and b in idx:
                return cosine(vs[idx[a]], vs[idx[b]])
            return None

    plan = []
    for nid in order:
        n = nodes[nid]
        entry = {"id": nid, "title": n["title"], "up": [], "down": [], "lateral": []}
        # up = parent; down = children (already in map); anchors from targets
        for u in n["internal_links"].get("up", []):
            if u in nodes:
                entry["up"].append({"target": u, "to": nodes[u]["title"],
                                    "anchors": anchors_for(nodes[u])})
        for d in n["internal_links"].get("down", []):
            if d in nodes:
                entry["down"].append({"target": d, "to": nodes[d]["title"],
                                      "anchors": anchors_for(nodes[d])})
        for l in n["internal_links"].get("lateral", []):
            if l not in nodes:
                continue
            just = "shared attribute / next-question (asserted)"
            prov = "asserted"
            if sim:
                s = sim(nid, l)
                if s is not None:
                    if s >= lateral_threshold:
                        just = f"embedding sim {round(s,3)} ≥ {lateral_threshold} (derived)"
                        prov = "derived"
                    else:
                        just = f"embedding sim {round(s,3)} < {lateral_threshold} — REVIEW (may be weak)"
                        prov = "derived"
            entry["lateral"].append({"target": l, "to": nodes[l]["title"],
                                     "anchors": anchors_for(nodes[l]),
                                     "justification": just, "provenance": prov})
        plan.append(entry)

    # orphan / over-link analysis over the *planned* internal graph
    incoming = {nid: 0 for nid in nodes}
    for nid in nodes:
        for grp in ("down", "lateral", "up"):
            for t in nodes[nid]["internal_links"].get(grp, []):
                if t in incoming:
                    incoming[t] += 1
    orphans = [nid for nid in nodes if incoming[nid] == 0]
    over = sorted(((nid, c) for nid, c in incoming.items() if c >= 8), key=lambda x: -x[1])

    # crawl-based real orphans (published pages with no incoming links), if provided
    real_orphans = []
    if crawl_dir and os.path.isdir(crawl_dir):
        import glob
        pages = [json.load(open(f)) for f in glob.glob(os.path.join(crawl_dir, "*.json"))]
        urlset = {p["url"] for p in pages}
        inc = {u: 0 for u in urlset}
        for p in pages:
            for l in p.get("links", []):
                for u in urlset:
                    if u != p["url"] and l.rstrip("/") == u.rstrip("/"):
                        inc[u] += 1
        real_orphans = [u for u in urlset if inc[u] == 0]

    return {"plan": plan, "orphans": orphans, "over_linked": over,
            "real_orphans": real_orphans}


def to_markdown(res, brand=""):
    md = [f"# Internal Linking Plan — {brand or 'site'}",
          "> Anchors are varied, descriptive suggestions from each target's query network "
          "(pick one per placement; avoid exact-match repetition).", ""]
    for e in res["plan"]:
        if not (e["up"] or e["down"] or e["lateral"]):
            continue
        md.append(f"### {e['title']}  `{e['id']}`")
        for grp, label in (("up", "↑ up"), ("down", "↓ down"), ("lateral", "↔ lateral")):
            for link in e[grp]:
                anchors = " · ".join(f'"{a}"' for a in link["anchors"])
                extra = f" — {link['justification']}" if grp == "lateral" else ""
                md.append(f"- {label} → **{link['to']}** (`{link['target']}`){extra}\n  anchors: {anchors}")
        md.append("")
    md.append("## Link-health flags")
    md.append(f"- Planned-graph orphans (no incoming links): {res['orphans'] or 'none'}")
    md.append(f"- Over-linked hubs (≥8 incoming): {[f'{n} ({c})' for n,c in res['over_linked']] or 'none'}")
    if res["real_orphans"]:
        md.append(f"- Crawl orphans (published, no incoming): {res['real_orphans']}")
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--vecs")
    ap.add_argument("--lateral-threshold", type=float, default=0.72)
    ap.add_argument("--crawl-dir")
    ap.add_argument("--brand", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = build(json.load(open(a.map)), a.vecs, a.lateral_threshold, a.crawl_dir)
    open(a.out, "w").write(to_markdown(res, a.brand))
    json.dump(res, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print(json.dumps({"out": a.out, "nodes_with_links": sum(1 for e in res["plan"] if e["up"] or e["down"] or e["lateral"]),
                      "orphans": len(res["orphans"]), "over_linked": len(res["over_linked"])}, indent=2))


if __name__ == "__main__":
    main()
