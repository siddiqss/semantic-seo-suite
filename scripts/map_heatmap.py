#!/usr/bin/env python3
"""
map_heatmap.py — render a topical-map.json into a single self-contained HTML file
showing the pillar/cluster/supporting tree coloured by coverage status. No server, no
external assets. Used by topical-map-builder (once statuses exist) and site-auditor.

Status colours: planned (grey), briefed (amber), drafted (blue), published (green),
needs-update (red). Core and outer sections are shown separately.

Usage:
  python map_heatmap.py --map brands/<slug>/topical-map.json --out heatmap.html
"""
from __future__ import annotations
import argparse, json, html

COLORS = {
    "planned": "#9aa0a6", "briefed": "#e8a13a", "drafted": "#4a90d9",
    "published": "#3fae5a", "needs-update": "#d9534f",
}


def build(map_obj):
    nodes = map_obj["nodes"]
    by_id = {n["id"]: n for n in nodes}
    children = {}
    for n in nodes:
        if n["parent"]:
            children.setdefault(n["parent"], []).append(n["id"])

    def chip(n):
        c = COLORS.get(n["status"], "#ccc")
        title = html.escape(n["title"])
        intent = html.escape(n["intent"])
        return (f'<div class="node {n["tier"]}" style="border-left:6px solid {c}">'
                f'<span class="dot" style="background:{c}"></span>'
                f'<b>{title}</b> <span class="meta">{n["tier"]} · {intent} · '
                f'<code>{n["id"]}</code> · <em>{html.escape(n["status"])}</em></span></div>')

    def render_tree(section):
        rows = []
        for p in [n for n in nodes if n["tier"] == "pillar" and n["section"] == section]:
            rows.append(f'<div class="lvl0">{chip(p)}')
            for cid in children.get(p["id"], []):
                rows.append(f'<div class="lvl1">{chip(by_id[cid])}')
                for sid in children.get(cid, []):
                    rows.append(f'<div class="lvl2">{chip(by_id[sid])}</div>')
                rows.append("</div>")
            rows.append("</div>")
        return "\n".join(rows)

    counts = {}
    for n in nodes:
        counts[n["status"]] = counts.get(n["status"], 0) + 1
    legend = " ".join(
        f'<span class="lg"><span class="dot" style="background:{COLORS[k]}"></span>{k} ({counts.get(k,0)})</span>'
        for k in COLORS)

    ce = html.escape(map_obj["central_entity"]["name"])
    return f"""<!doctype html><meta charset="utf-8">
<title>Topical map heatmap — {ce}</title>
<style>
 body{{font:14px/1.5 system-ui,Segoe UI,Roboto,sans-serif;margin:24px;color:#1a1a1a;background:#fafafa}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#666;margin-bottom:16px}}
 .legend{{margin:12px 0 20px}} .lg{{margin-right:14px;white-space:nowrap}}
 .dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}}
 h2{{font-size:15px;border-bottom:1px solid #ddd;padding-bottom:4px;margin-top:28px}}
 .node{{background:#fff;border-radius:6px;padding:6px 10px;margin:4px 0;box-shadow:0 1px 2px rgba(0,0,0,.06)}}
 .meta{{color:#666;font-size:12px}} code{{background:#f0f0f0;padding:0 4px;border-radius:3px}}
 .lvl1{{margin-left:26px}} .lvl2{{margin-left:52px}}
 .pillar b{{font-size:15px}}
</style>
<h1>Topical map heatmap — {ce}</h1>
<div class="sub">Grounding tier: {html.escape(map_obj.get('grounding_tier','?'))} · {len(nodes)} nodes · generated {html.escape(map_obj.get('generated','?'))}</div>
<div class="legend">{legend}</div>
<h2>Core section (monetizing)</h2>
{render_tree('core')}
<h2>Outer section (authority feeders)</h2>
{render_tree('outer')}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    html_str = build(json.load(open(a.map)))
    open(a.out, "w").write(html_str)
    print(f"wrote {a.out} ({len(html_str)} bytes)")


if __name__ == "__main__":
    main()
