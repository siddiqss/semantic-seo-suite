#!/usr/bin/env python3
"""
audit_site.py — analyse a crawled site against its topical map.

Ties together the T1 primitives (embed_corpus, semantic_distance) plus the draft lint
(validate_draft) to produce a semantic site audit: coverage gaps, keyword
cannibalization, entity drift, orphan pages, and per-page micro-issues. Everything is
provenance-labelled; nothing is invented.

Inputs:
  --map            topical-map.json
  --crawl-dir      directory of page JSONs from extract_page_content.py
  --entity-profile entity-profile.json (for the claimed-identity centroid)
  --locked         locked-facts.json (for the micro-audit brand check)  [optional]
  --brand          brand display name (for micro-audit)                 [optional]
  --out            audit report markdown path
  --cannibal-threshold / --match-threshold / --drift-threshold          [tunable]
  --fallback       force offline hashing embeddings (default: try model, fall back)

Output: a markdown audit report (from templates/audit-report.template.md structure) and
a JSON sidecar with machine-readable findings + suggested map status updates.

Runs fully offline with --fallback (coarse embeddings). For real decisions run with a
model embedding backend.
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embed_corpus import embed          # noqa: E402
from semantic_distance import cosine    # noqa: E402
import validate_draft as vd             # noqa: E402


def load_pages(crawl_dir):
    pages = []
    for f in sorted(glob.glob(os.path.join(crawl_dir, "*.json"))):
        d = json.load(open(f))
        heads = " . ".join(h.get("text", "") for h in d.get("headings", []))
        body = d.get("body", "")[:1200]
        d["_text"] = f"{d.get('title','')} . {' '.join(d.get('h1',[]))} . {heads} . {body}"
        d["_intent"] = guess_intent(d)  # coarse, asserted
        pages.append(d)
    return pages


def guess_intent(page):
    t = (page.get("title", "") + " " + " ".join(h.get("text", "") for h in page.get("headings", []))).lower()
    if re.search(r"\b(buy|price|pricing|shop|order|deal)\b", t):
        return "transactional"
    if re.search(r"\b(best|top \d|review|vs|compare|comparison|alternative)\b", t):
        return "commercial"
    return "informational"


def embed_all(texts, force_fallback):
    items = [{"id": str(i), "text": t} for i, t in enumerate(texts)]
    ids, vecs, dim, backend = embed(items, force_fallback=force_fallback)
    return vecs, backend


def claimed_centroid(node_vecs, node_meta, ep):
    """Centroid of core-section node vectors = the site's intended topical centre."""
    idxs = [i for i, n in enumerate(node_meta) if n["section"] == "core"]
    if not idxs:
        idxs = list(range(len(node_meta)))
    d = len(node_vecs[0])
    c = [sum(node_vecs[i][k] for i in idxs) / len(idxs) for k in range(d)]
    import math
    norm = math.sqrt(sum(x * x for x in c)) or 1.0
    return [x / norm for x in c]


def run(map_path, crawl_dir, ep_path, locked, brand, cannibal_t, match_t, drift_t, force_fallback):
    m = json.load(open(map_path))
    nodes = m["nodes"]
    node_texts = [n["title"] + " . " + " . ".join(q["query"] for q in n.get("query_network", [])) for n in nodes]
    pages = load_pages(crawl_dir)
    ep = json.load(open(ep_path)) if ep_path and os.path.exists(ep_path) else {}

    node_vecs, backend = embed_all(node_texts, force_fallback)
    page_vecs, _ = embed_all([p["_text"] for p in pages], force_fallback) if pages else ([], backend)

    # 1) URL -> node matching (each page to its nearest node)
    matches = {}   # node_id -> [(page_idx, sim)]
    page_match = []
    for pi, pv in enumerate(page_vecs):
        best_ni, best = -1, -1.0
        for ni, nv in enumerate(node_vecs):
            s = cosine(pv, nv)
            if s > best:
                best, best_ni = s, ni
        page_match.append((best_ni, best))
        if best >= match_t:
            matches.setdefault(nodes[best_ni]["id"], []).append((pi, round(best, 4)))

    # 2) gaps = nodes with no matched page
    gaps = [{"id": n["id"], "title": n["title"], "tier": n["tier"], "section": n["section"],
             "provenance": "derived"} for n in nodes if n["id"] not in matches]

    # 3) cannibalization = page pairs, high sim + same coarse intent; OR two pages hitting one node
    cannibal = []
    for i in range(len(pages)):
        for j in range(i + 1, len(pages)):
            s = cosine(page_vecs[i], page_vecs[j])
            if s >= cannibal_t and pages[i]["_intent"] == pages[j]["_intent"]:
                cannibal.append({"a": pages[i]["url"], "b": pages[j]["url"],
                                 "similarity": round(s, 4), "signal": "embedding+intent",
                                 "provenance": "derived"})
    for nid, ms in matches.items():
        if len(ms) > 1:
            urls = [pages[pi]["url"] for pi, _ in ms]
            cannibal.append({"a": urls[0], "b": ", ".join(urls[1:]), "similarity": None,
                             "signal": f"multiple pages map to node {nid}", "provenance": "derived"})

    # 4) entity drift = pages farthest from the claimed (core) centroid
    drift = []
    if pages:
        cc = claimed_centroid(node_vecs, nodes, ep)
        scored = [(pages[pi]["url"], round(1 - cosine(page_vecs[pi], cc), 4)) for pi in range(len(pages))]
        scored.sort(key=lambda x: -x[1])
        for url, dist in scored:
            if dist >= drift_t:
                drift.append({"url": url, "distance_from_center": dist, "provenance": "derived"})

    # 5) orphans = pages with no incoming internal link from other crawled pages
    urlset = {p["url"] for p in pages}
    incoming = {u: 0 for u in urlset}
    for p in pages:
        for l in p.get("links", []):
            for u in urlset:
                if u != p["url"] and (l == u or l.rstrip("/") == u.rstrip("/")):
                    incoming[u] += 1
    orphans = [{"url": u, "incoming": incoming[u], "provenance": "measured"}
               for u in urlset if incoming[u] == 0]

    # 6) micro-audit (lint each page body with the draft rules)
    micro = []
    brand_terms = [brand] if brand else []
    locked_index, locked_vals = {}, set()
    if locked and os.path.exists(locked):
        for f in json.load(open(locked)).get("facts", []):
            locked_index[f["key"]] = f; locked_vals.add(str(f.get("value", "")))
    for p in pages:
        v = []
        vd.check_stats(p.get("body", ""), [], locked_vals, v)
        vd.check_lint(p.get("body", ""), v)
        highs = [x for x in v if x["severity"] == "high"]
        if v:
            micro.append({"url": p["url"], "high": len(highs), "warn": len(v) - len(highs),
                          "issues": [f"{x['check']}: {x['detail']}" for x in v[:4]], "provenance": "measured"})

    # suggested map status updates
    status_updates = []
    for nid, ms in matches.items():
        status_updates.append({"id": nid, "url": pages[ms[0][0]]["url"], "status": "published"})

    return {
        "backend": backend, "pages": len(pages), "nodes": len(nodes),
        "coverage": {"covered": len(matches), "gaps": len(gaps)},
        "gaps": gaps, "cannibalization": cannibal, "drift": drift,
        "orphans": orphans, "micro": micro, "status_updates": status_updates,
    }


def to_markdown(res, brand):
    def rows(items, cols):
        return "\n".join("| " + " | ".join(str(i.get(c, "")) for c in cols) + " |" for i in items) or "| _none_ |" + " |" * (len(cols) - 1)
    md = [f"# Semantic Site Audit — {brand or 'site'}",
          f"Backend: **{res['backend']}** · Pages: {res['pages']} · Nodes: {res['nodes']}",
          "",
          "> All findings are provenance-tagged. `measured` = from crawl. `derived` = computed from embeddings.",
          f"\n## Summary\n- Coverage: **{res['coverage']['covered']} covered · {res['coverage']['gaps']} gaps**"
          f"\n- Cannibalization pairs: **{len(res['cannibalization'])}**"
          f"\n- Drift pages: **{len(res['drift'])}** · Orphans: **{len(res['orphans'])}**"
          f" · Pages with micro-issues: **{len(res['micro'])}**",
          "\n## 1. Coverage gaps (map nodes with no matching page)",
          "| id | title | tier | section |\n|---|---|---|---|",
          rows(res["gaps"][:40], ["id", "title", "tier", "section"]),
          "\n## 2. Cannibalization",
          "| Page A | Page B | Similarity | Signal |\n|---|---|---|---|",
          rows(res["cannibalization"], ["a", "b", "similarity", "signal"]),
          "\n## 3. Entity drift (pages farthest from the core topical centre)",
          "| URL | Distance | Provenance |\n|---|---|---|",
          rows(res["drift"], ["url", "distance_from_center", "provenance"]),
          "\n## 4. Orphan pages (no incoming internal links)",
          "| URL | Incoming |\n|---|---|",
          rows(res["orphans"], ["url", "incoming"]),
          "\n## 5. Micro-semantic issues",
          "| URL | High | Warn | Sample issues |\n|---|---|---|---|",
          "\n".join(f"| {mi['url']} | {mi['high']} | {mi['warn']} | {'; '.join(mi['issues'])} |" for mi in res["micro"]) or "| _none_ |  |  |  |",
          "\n## 6. Prioritised actions"]
    # recommendations
    recs = []
    for g in res["gaps"][:8]:
        recs.append(f"1. **create** — {g['title']} (`{g['id']}`, {g['section']}/{g['tier']}) — coverage gap.")
    for c in res["cannibalization"][:5]:
        recs.append(f"1. **consolidate/redirect** — {c['a']} vs {c['b']} — {c['signal']}.")
    for d in res["drift"][:3]:
        recs.append(f"1. **rewrite/relink or prune** — {d['url']} — far from core centre ({d['distance_from_center']}).")
    for o in res["orphans"][:3]:
        recs.append(f"1. **relink** — {o['url']} — orphan, add incoming internal links.")
    md.append("\n".join(recs) or "_No actions._")
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--crawl-dir", required=True)
    ap.add_argument("--entity-profile")
    ap.add_argument("--locked")
    ap.add_argument("--brand", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cannibal-threshold", type=float, default=0.86)
    ap.add_argument("--match-threshold", type=float, default=0.55)
    ap.add_argument("--drift-threshold", type=float, default=0.55)
    ap.add_argument("--fallback", action="store_true")
    a = ap.parse_args()
    res = run(a.map, a.crawl_dir, a.entity_profile, a.locked, a.brand,
              a.cannibal_threshold, a.match_threshold, a.drift_threshold, a.fallback)
    open(a.out, "w").write(to_markdown(res, a.brand))
    json.dump(res, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print(json.dumps({"out": a.out, "backend": res["backend"], **res["coverage"],
                      "cannibalization": len(res["cannibalization"]),
                      "drift": len(res["drift"]), "orphans": len(res["orphans"])}, indent=2))


if __name__ == "__main__":
    main()
