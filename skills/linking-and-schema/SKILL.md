---
name: linking-and-schema
description: >
  Generate an internal-linking plan and JSON-LD structured data from a brand's topical
  map and entity profile. Use whenever the user asks about internal links, anchor text,
  site structure, linking strategy, schema markup, structured data, or JSON-LD — or right
  after new content is drafted or published. Produces an actionable link checklist (with
  varied anchors) and validated per-node schema files. Triggers on linking/schema intent
  broadly.
---

# linking-and-schema

Turn the map into a link graph and structured data. Both outputs are deterministic and
carry the framework's fact discipline: laterals are justified (not sprayed), anchors are
varied (not exact-match spam), and schema never states an ungrounded fact.

Read first: `../../framework/internal-linking-rules.md`, `../../framework/schema-jsonld.md`,
`../../framework/eeat-signals.md`.

## Preconditions
- `topical-map.json` and `entity-profile.json` for the brand.
- Optional: map embeddings (for lateral justification) and crawl data (for real orphans).

## Workflow

1. **Internal-linking plan:**
   ```
   python ../../scripts/linking_plan.py --map brands/<slug>/topical-map.json \
     [--vecs brands/<slug>/data/embeddings/map.npz --lateral-threshold 0.72] \
     [--crawl-dir brands/<slug>/data/crawl] --brand "<Brand>" \
     --out brands/<slug>/audits/linking-plan.md
   ```
   For each node it emits up/down/justified-lateral links with varied, descriptive
   anchors drawn from the target's query network, plus link-health flags (planned-graph
   orphans, over-linked hubs, and real crawl orphans if crawl data is present). Laterals
   below the embedding threshold are marked REVIEW rather than dropped or trusted.

2. **JSON-LD schema:**
   ```
   python ../../scripts/schema_jsonld.py --map brands/<slug>/topical-map.json \
     --entity-profile brands/<slug>/entity-profile.json \
     --locked brands/<slug>/locked-facts.json \
     --out-dir brands/<slug>/data/schema
   ```
   Emits one `.jsonld` per node (HowTo / FAQPage / Product / Article), a site-level
   `Organization` graph, and a `checklist.md`. Product `Offer` prices come ONLY from
   locked facts; FAQ/HowTo answer text is left as a placeholder to be filled from the
   *validated* draft — so no invented answer ships in markup.

3. **Hand off:** give the user the link checklist (page → insert link → suggested
   anchor → where) and the schema files. Note that syntactic validation here is
   necessary but not sufficient — run Google's Rich Results Test before publishing.

## Definition of done
- Link plan covers every node; laterals justified; orphans/over-links flagged.
- One schema file per node + org graph; 0 validation issues; no fabricated price/rating.
- Anchors are varied across placements (no exact-match repetition).

## Grounding ladder
- **T0:** link plan from map structure; laterals justified by named shared attribute
  (`asserted`). Schema from map + profile.
- **T1:** laterals justified by embedding distance (`derived`); real orphans from crawl.
- **Author `Person` schema** is emitted only when a real author/credential exists
  (eeat-signals.md) — never fabricated to fill the template.
