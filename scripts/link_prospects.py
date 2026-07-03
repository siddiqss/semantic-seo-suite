#!/usr/bin/env python3
"""
link_prospects.py — off-page link-opportunity planner for the link-opportunities skill.

The suite's on-page half (linking_plan.py) wires *internal* links. This plans *external*
link acquisition: which link-building plays fit each topical-map node, a safe off-page
anchor-text mix, and a competitor-backlink-gap worksheet seeded from the entity profile.

It is deterministic and offline. It does NOT invent prospects: real referring domains,
authority numbers, and contact emails are discovered at run time by the skill via
web_search (T1) or DataForSEO backlinks (T2) and recorded with provenance. This script
produces the plan skeleton + scoring so those real prospects can be prioritized honestly.

Anti-fabrication rule baked in: score_prospect treats unknown authority as unknown
(never 0, never a guess) and the worksheet header forbids invented DA / emails.

Usage:
  python link_prospects.py --map brands/<slug>/topical-map.json \
      --entity-profile brands/<slug>/entity-profile.json --brand "<Brand>" --out plan.md
  python link_prospects.py --selftest
"""
from __future__ import annotations
import argparse, json, re, sys

# Off-page anchor mix — deliberately low exact-match (over-optimized external anchors are
# a penalty risk, unlike internal anchors). Fractions must sum to 1.0.
ANCHOR_MIX = {"branded": 0.40, "natural/generic": 0.25, "topic/partial": 0.25, "exact-match": 0.10}

# Link plays keyed to node shape. (name, applies_to, note)
PLAYS = [
    ("listicle-inclusion", "commercial", "Get added to existing 'best/ top AI UGC tool' roundups that already rank."),
    ("competitor-backlink-gap", "commercial", "Pull who links to each competitor; pitch the same sites."),
    ("comparison/review", "commercial", "Reviewers & comparison sites covering this category."),
    ("resource-page", "informational", "Curated resource/guide pages in DTC & paid-social niches."),
    ("digital-PR/data", "informational", "Journalists/newsletters — pitch a locked stat or original data."),
    ("guest-post", "outer", "Contributed posts on ecommerce/marketing blogs; link the pillar."),
    ("community", "informational", "Reddit/Quora/Slack answers — usually nofollow, but drive referral + AI citation."),
]

def anchor_examples(node, brand):
    """Concrete example anchors per style, from the node's target query + brand."""
    tq = node.get("target_query", node["title"]).strip()
    head = tq.split()[:3]
    return {
        "branded": [brand, f"{brand}'s guide", f"{brand} ({tq})"],
        "natural/generic": ["this guide", "a detailed breakdown", "here"],
        "topic/partial": [" ".join(head), f"{tq} explained", f"how {tq}"],
        "exact-match": [tq],  # use sparingly — see ANCHOR_MIX
    }

def priority(node):
    """Derived priority: core beats outer, pillar beats cluster beats supporting."""
    sect = {"core": 2, "outer": 1}.get(node.get("section"), 0)
    tier = {"pillar": 3, "cluster": 2, "supporting": 1}.get(node.get("tier"), 0)
    return sect * 10 + tier

def plays_for(node):
    out = []
    for name, applies, note in PLAYS:
        if applies == node.get("intent") or applies == node.get("section") or (
           applies == "commercial" and node.get("intent") == "commercial"):
            out.append({"play": name, "note": note})
    # every node can use resource-page / community; ensure at least one play
    if not out:
        out.append({"play": "resource-page", "note": dict((p[0], p[2]) for p in PLAYS)["resource-page"]})
    return out

def score_prospect(relevance, authority, dofollow, link_type_weight=1.0):
    """Prioritize a REAL discovered prospect. relevance in [0,1]; authority in [0,100] or
    None when unknown (do NOT pass a guess). Returns (score, authority_known)."""
    if not 0 <= relevance <= 1:
        raise ValueError("relevance must be 0..1")
    base = relevance * 60 * link_type_weight
    base += 20 if dofollow else 5
    if authority is None:
        return round(base, 1), False           # unknown authority: score on what we know
    if not 0 <= authority <= 100:
        raise ValueError("authority must be 0..100 or None")
    return round(base + authority * 0.2, 1), True

def build(map_obj, profile, brand):
    nodes = sorted(map_obj["nodes"], key=priority, reverse=True)
    plan = []
    for n in nodes:
        plan.append({
            "id": n["id"], "title": n["title"], "section": n.get("section"),
            "tier": n.get("tier"), "intent": n.get("intent"),
            "priority": priority(n), "url": n.get("url"),
            "plays": plays_for(n),
            "anchor_examples": anchor_examples(n, brand),
        })
    competitors = [{"name": c["name"], "domain": c.get("domain")}
                   for c in profile.get("competitors", [])]
    return {"brand": brand, "anchor_mix": ANCHOR_MIX,
            "competitor_backlink_gap": competitors, "plan": plan}

def to_markdown(res):
    b = res["brand"]
    md = [f"# Link-Opportunity Plan — {b}", "",
          "> DO NOT FABRICATE. Never invent a domain authority number, a referring domain,",
          "> or a contact email. Discover prospects via web_search (T1) or DataForSEO",
          "> backlinks (T2) and tag each `measured` with the date. Unknown authority stays",
          "> unknown — see score_prospect.", "",
          "## Off-page anchor mix (target distribution)"]
    md.append(" · ".join(f"{k} {int(v*100)}%" for k, v in res["anchor_mix"].items()))
    md.append("_Keep exact-match low; external over-optimization is a penalty risk._")
    md += ["", "## Competitor backlink-gap worksheet (seed for T2 pull)"]
    for c in res["competitor_backlink_gap"]:
        md.append(f"- {c['name']} (`{c.get('domain','?')}`) → list referring domains, "
                  f"filter for topical relevance, pitch the same.")
    md += ["", "## Prioritized node plays"]
    for e in res["plan"]:
        tag = f"{e['tier']} · {e['section']} · {e['intent']} · prio {e['priority']}"
        md.append(f"\n### {e['title']}  (`{e['id']}`)\n{tag}")
        for p in e["plays"]:
            md.append(f"- **{p['play']}** — {p['note']}")
        ax = e["anchor_examples"]
        md.append("  anchors: " + " | ".join(
            f"{k}: " + ", ".join(f'"{x}"' for x in v[:2]) for k, v in ax.items()))
    return "\n".join(md) + "\n"

def selftest():
    core_pillar = {"section": "core", "tier": "pillar", "intent": "commercial"}
    outer_supp = {"section": "outer", "tier": "supporting", "intent": "informational"}
    assert priority(core_pillar) > priority(outer_supp)
    # exact-match is the smallest slice of the anchor mix
    assert ANCHOR_MIX["exact-match"] == min(ANCHOR_MIX.values())
    assert abs(sum(ANCHOR_MIX.values()) - 1.0) < 1e-9
    # score rises with relevance; unknown authority flagged, not zeroed into a guess
    s_lo, _ = score_prospect(0.2, None, True)
    s_hi, known = score_prospect(0.9, None, True)
    assert s_hi > s_lo and known is False
    # known authority raises score and is flagged known
    s_auth, known2 = score_prospect(0.5, 80, True)
    assert known2 is True and s_auth > score_prospect(0.5, None, True)[0]
    print("selftest ok — priority + anchor-mix + honest-scoring invariants hold")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map"); ap.add_argument("--entity-profile")
    ap.add_argument("--brand", default=""); ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if not (a.map and a.entity_profile and a.out):
        print("error: --map, --entity-profile, --out required", file=sys.stderr); sys.exit(2)
    res = build(json.load(open(a.map)), json.load(open(a.entity_profile)), a.brand)
    open(a.out, "w").write(to_markdown(res))
    json.dump(res, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print(json.dumps({"out": a.out, "nodes": len(res["plan"]),
                      "competitors": len(res["competitor_backlink_gap"])}, indent=2))

if __name__ == "__main__":
    main()
