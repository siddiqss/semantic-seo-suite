#!/usr/bin/env python3
"""
schema_jsonld.py — generate JSON-LD structured data from the topical map + entity
profile, and validate it syntactically.

Node → schema type mapping (schema-jsonld.md):
  intent transactional / commercial + product entity  -> Product (+ Offer if locked price)
  question-style node / FAQ-shaped                     -> FAQPage
  how-to node                                          -> HowTo
  everything else                                      -> Article
Plus a site-level Organization + Person (author) graph from the entity profile / EEAT.

Facts rule: an Offer price is emitted ONLY if a matching locked-facts entry exists —
never invent a price into schema. Ratings/reviews are NEVER fabricated.

Usage:
  python schema_jsonld.py --map map.json --entity-profile ep.json \
     [--locked locked-facts.json] --out-dir brands/<slug>/data/schema
"""
from __future__ import annotations
import argparse, json, os, re


def node_type(n):
    title = n["title"].lower()
    if re.search(r"\bhow to\b|step by step|guide\b", title) and n["intent"] == "informational":
        return "HowTo"
    if title.strip().endswith("?") or n.get("target_query", "").lower().startswith(("what", "why", "how", "is ", "are ")):
        return "FAQPage"
    if n["intent"] in ("transactional", "commercial") and n["section"] == "core":
        return "Product"
    return "Article"


def org_person_graph(ep):
    sc = ep.get("source_context", {})
    graph = []
    org = {"@type": "Organization", "name": ep.get("brand", ""),
           "url": f"https://{ep.get('domain','')}", "description": sc.get("what", "")}
    graph.append(org)
    # Author/Person only if the profile carries a real credential; otherwise omit
    # (never fabricate an author). Left as a template hook.
    return graph


def build_node_schema(n, ep, locked_index):
    t = node_type(n)
    url = n.get("url") or f"https://{ep.get('domain','')}/{n['id']}"
    base = {"@context": "https://schema.org", "@type": t, "name": n["title"], "url": url}
    if t == "Article":
        base["about"] = [e["entity"] for e in n.get("entities", [])][:5]
    elif t == "FAQPage":
        base["mainEntity"] = [{"@type": "Question", "name": q["query"],
                               "acceptedAnswer": {"@type": "Answer", "text": "<answer from draft>"}}
                              for q in n.get("query_network", [])[:5]]
    elif t == "HowTo":
        base["step"] = [{"@type": "HowToStep", "name": q["query"]} for q in n.get("query_network", [])[:6]]
    elif t == "Product":
        base["category"] = ep.get("central_entity", {}).get("name", "")
        # Offer ONLY from locked facts — never invented
        price_fact = next((f for k, f in locked_index.items() if "price" in k or "pricing" in k), None)
        if price_fact and price_fact.get("value") not in (None, "", "null"):
            base["offers"] = {"@type": "Offer", "price": price_fact["value"],
                              "priceCurrency": "USD", "_source": price_fact["source"]}
        else:
            base["_note"] = "No locked price fact; Offer omitted (never fabricate a price)."
    return base


def validate(obj):
    """Syntactic checks: JSON-serialisable, required keys present."""
    issues = []
    try:
        json.dumps(obj)
    except TypeError as e:
        issues.append(f"not serialisable: {e}")
    if "@context" not in obj or "@type" not in obj:
        issues.append("missing @context/@type")
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--entity-profile", required=True)
    ap.add_argument("--locked")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    m = json.load(open(a.map)); ep = json.load(open(a.entity_profile))
    locked_index = {}
    if a.locked and os.path.exists(a.locked):
        for f in json.load(open(a.locked)).get("facts", []):
            locked_index[f["key"]] = f

    # site graph
    graph = {"@context": "https://schema.org", "@graph": org_person_graph(ep)}
    json.dump(graph, open(os.path.join(a.out_dir, "_organization.jsonld"), "w"), indent=2)

    counts, issues_total = {}, 0
    checklist = ["# Schema checklist", ""]
    for n in m["nodes"]:
        s = build_node_schema(n, ep, locked_index)
        counts[s["@type"]] = counts.get(s["@type"], 0) + 1
        issues = validate(s)
        issues_total += len(issues)
        json.dump(s, open(os.path.join(a.out_dir, f"{n['id']}.jsonld"), "w"), indent=2)
        flag = " ⚠ " + "; ".join(issues) if issues else ""
        checklist.append(f"- `{n['id']}` {n['title']} → **{s['@type']}**{flag}")
    open(os.path.join(a.out_dir, "checklist.md"), "w").write("\n".join(checklist))
    print(json.dumps({"out_dir": a.out_dir, "by_type": counts,
                      "validation_issues": issues_total,
                      "org_graph": "_organization.jsonld"}, indent=2))


if __name__ == "__main__":
    main()
