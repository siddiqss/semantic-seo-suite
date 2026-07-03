#!/usr/bin/env python3
"""
distribution_plan.py — content-distribution planner for the content-distribution skill.

The map decides WHAT to publish; this decides how each published piece gets SEEN.
Deterministic and offline: for every node it derives fitting channels (from the brand's
audience/personas + the node's intent/section), the repurposing atoms to cut from the
piece, and a cadence anchored to publishing. Published nodes are promoted first.

Honesty rule (suite overlay): this emits no reach/engagement numbers — there is nothing
to measure yet. Specific communities/newsletters are discovered by the skill via
web_search (T1) and recorded `measured`; the script only proposes channel *types*.

Usage:
  python distribution_plan.py --map brands/<slug>/topical-map.json \
      --entity-profile brands/<slug>/entity-profile.json --brand "<Brand>" --out dist-plan.md
  python distribution_plan.py --selftest
"""
from __future__ import annotations
import argparse, json, sys

# Repurposing atoms — one published piece becomes many; formats, not fabricated content.
ATOMS = [
    "X/Twitter thread from the question-H2 answers",
    "LinkedIn founder POV post (the one insight)",
    "Reddit/Quora answer that links back contextually",
    "Short-form video (dogfood the product) from the hook",
    "Newsletter section",
    "Carousel / infographic from a list or table in the piece",
]

def priority(node):
    """Promote what's live first; then core over outer, pillar over cluster."""
    live = 100 if node.get("status") == "published" else 0
    sect = {"core": 2, "outer": 1}.get(node.get("section"), 0)
    tier = {"pillar": 3, "cluster": 2, "supporting": 1}.get(node.get("tier"), 0)
    return live + sect * 5 + tier

def channels(node):
    base = ["Owned: newsletter", "Owned: X/Twitter", "Owned: LinkedIn",
            "Community: Reddit/Quora (where the ICP asks)"]
    if node.get("intent") == "commercial":
        base += ["Paid: retarget warm audiences with this asset",
                 "Earned: roundup/listicle inclusion (hand to link-opportunities)"]
    if node.get("section") == "outer" or node.get("tier") == "pillar":
        base += ["Syndication: Medium / LinkedIn article",
                 "Hacker News / niche aggregators (only if genuinely novel)"]
    return base

def cadence(node):
    if node.get("status") == "published":
        return "Day 0: owned + community · Day 3-7: syndication · Monthly: evergreen re-share"
    return "Queue atoms now; fire on the node's publish week (see calendar.md)"

def build(map_obj, profile, brand):
    nodes = sorted(map_obj["nodes"], key=priority, reverse=True)
    audience = profile.get("source_context", {}).get("audience", [])
    personas = [p.get("name") for p in profile.get("personas", [])]
    plan = [{
        "id": n["id"], "title": n["title"], "status": n.get("status"),
        "section": n.get("section"), "tier": n.get("tier"), "intent": n.get("intent"),
        "priority": priority(n), "url": n.get("url"),
        "channels": channels(n), "atoms": ATOMS, "cadence": cadence(n),
    } for n in nodes]
    return {"brand": brand, "audience": audience, "personas": personas, "plan": plan}

def to_markdown(res):
    md = [f"# Content Distribution Plan — {res['brand']}", "",
          "> No invented reach/engagement numbers. Find the *specific* subreddits,",
          "> newsletters, and communities your ICP uses via web_search (T1) and record",
          "> them `measured` + dated. This plan proposes channel types + repurposing.", "",
          "**Audience:** " + ("; ".join(res["audience"]) or "—"),
          "**Personas:** " + (", ".join(p for p in res["personas"] if p) or "—"), "",
          "## Priority order (published first, then core→outer)"]
    for e in res["plan"]:
        flag = "🟢 live" if e["status"] == "published" else "⚪ planned"
        md.append(f"\n### {e['title']}  (`{e['id']}`) — {flag}")
        md.append(f"{e['tier']} · {e['section']} · {e['intent']} · prio {e['priority']}")
        md.append("channels: " + " | ".join(e["channels"]))
        md.append("cadence: " + e["cadence"])
        md.append("atoms: " + "; ".join(e["atoms"]))
    return "\n".join(md) + "\n"

def selftest():
    live_core = {"status": "published", "section": "core", "tier": "pillar", "intent": "commercial"}
    plan_outer = {"status": "planned", "section": "outer", "tier": "supporting", "intent": "informational"}
    assert priority(live_core) > priority(plan_outer)
    # commercial nodes get a paid-amplification channel; pure outer-informational doesn't
    assert any("Paid" in c for c in channels(live_core))
    assert not any("Paid" in c for c in channels(plan_outer))
    # every node yields repurposing atoms
    assert len(ATOMS) >= 3
    # cadence differs by publish status
    assert cadence(live_core) != cadence(plan_outer)
    print("selftest ok — priority + channel-fit + cadence invariants hold")

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
                      "published": sum(1 for e in res["plan"] if e["status"] == "published")}, indent=2))

if __name__ == "__main__":
    main()
