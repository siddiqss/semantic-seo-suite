---
name: topical-map-builder
description: >
  Build or extend a full topical map — a pillar/cluster/supporting content architecture
  grounded in entity-based semantic SEO — for a brand. Use whenever the user asks for a
  topical map, a content plan or content strategy, keyword clustering into topics, "what
  should we write about", niche coverage, or how to build topical authority — even if
  they only mention keywords or blog ideas. Produces topical-map.json plus a readable
  tree and a prioritised content calendar. If the brand has no entity-profile.json,
  run seo-brand-foundation first. Triggers on content-planning intent broadly, not just
  the literal phrase "topical map".
---

# topical-map-builder

Turn a brand's foundation into an executable content architecture: a *processed*
topical map of pillars → clusters → supporting pages, each with an intent and a query
network, split into core (monetizing) and outer (authority-feeding) sections.

Read these first: `../../framework/topical-map-theory.md`,
`../../framework/eav-modeling.md`, `../../framework/query-semantics.md`. (And
`00-overview.md` for provenance rules if not already this session.)

## Preconditions
1. Read `brands/<slug>/config.yaml` (tier).
2. Require `brands/<slug>/entity-profile.json`. If absent, run **seo-brand-foundation**
   first — do not build a map without a foundation.

## Workflow

1. **Decompose the central entity (raw map).** Using the entity profile's attribute
   inventory + eav-modeling.md, over-generate: every attribute → candidate topics;
   values/comparisons/how-tos → sub-topics; questions/edge-cases → supporting topics;
   neighbouring entities → outer topics. Completeness first; don't filter yet.

2. **Apply the core/outer split** from the entity profile's boundary rule. Tag each
   candidate `core` or `outer`. Drop anything failing the "right to cover" test
   (source-context.md) — respect the will-not-cover list.

3. **Expand query networks** per node (query-semantics.md), at the configured tier:
   - T0: reason out the network + validate a few via `web_search`; intent `asserted`.
   - T1: `../../scripts/fetch_autocomplete.py` (real variants, `measured`),
     optional `../../scripts/fetch_trends.py` (relative demand), and
     `../../scripts/serp_intent_classifier.py` to upgrade intent to `measured`.
   - T2: `../../scripts/dataforseo_client.py` for volume/difficulty/PAA (`measured`).
   Never invent search volumes.

4. **Process the map:** assign `tier` (pillar/cluster/supporting), `parent`, and one
   `intent` per node. Merge near-duplicates:
   - T1+: `../../scripts/cluster_keywords.py` on query networks → flag & merge sibling
     pairs above `cannibalization_threshold`.
   - T0: merge by judgement (one URL, one intent).

5. **Attach demand + priority.** Set `volume`/`difficulty` only if grounded (tagged).
   Compute `priority ≈ business_value × demand_signal × feasibility`
   (topical-map-theory.md). At T0, demand is qualitative — priority_score may be
   `asserted` or left null with an ordering rationale.

6. **Wire internal links** (skeleton): each node's `up` (to parent), `down` (to
   children), and candidate `lateral` (siblings sharing an attribute; justify by
   embedding distance at T1). Full plan is `linking-and-schema`'s job later — here just
   seed structure.

7. **Emit artifacts.**
   - `brands/<slug>/topical-map.json` — must validate against
     `../../templates/topical-map.schema.json`.
   - A readable Markdown tree (write to `brands/<slug>/topical-map.md`).
   - Prioritised `brands/<slug>/calendar.md` from `../../templates/calendar.template.md`.
   - T1+: render the coverage heatmap via `../../scripts/map_heatmap.py`.

## Definition of done (gate for P1-18)
- ≥1 pillar per defining/unique attribute of the central entity.
- Every node has tier, section, parent (except top pillars), target query, query
  network, and intent (with provenance).
- No sibling pair above the cannibalization threshold.
- Every outer node has a link path into the core.
- Priority order + seeded calendar exist.
- The map passes an expert sniff test: no generic filler, core/outer reflects the
  actual business. If it reads generic, the fix is usually in the framework docs or the
  entity profile, not in prompt wording.

## Grounding ladder
- **T0:** structure + query networks by reasoning; intents/volumes `asserted`/absent.
- **T1:** autocomplete-grounded query networks, SERP-verified intents, embedding-based
  dedupe + lateral-link justification, relative demand.
- **T2:** absolute volume/difficulty + PAA from DataForSEO.
