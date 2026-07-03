---
name: content-brief-generator
description: >
  Generate entity-aware, Koray-style content briefs from a topical-map node or any
  target query — a semantically ordered heading skeleton with entity/attribute tags,
  internal-link targets, snippet target, word budgets, locked-facts references, and a
  do-not-fabricate list. Use whenever the user asks for a content brief, an article
  outline, writer instructions, "brief for X", or wants to start writing an article
  that exists in the topical map. Runs SERP recon first. Triggers on outline/brief
  intent broadly, not just the word "brief".
---

# content-brief-generator

Produce a brief a stranger writer could execute without further explanation, built on
the page's contextual vector (heading order = meaning) and locked to one macro context.

Read first: `../../framework/contextual-vectors.md`,
`../../framework/macro-micro-semantics.md`, `../../framework/query-semantics.md`,
`../../framework/internal-linking-rules.md`.

## Preconditions
- `brands/<slug>/config.yaml` (tier).
- A node in `brands/<slug>/topical-map.json` (or create an ad-hoc node from a query).

## Workflow

1. **Load the node** (target query, intent, entities, query network, internal links).
   If ad-hoc, first decompose the query's entity via `../../framework/eav-modeling.md`.

2. **SERP recon** for the target query:
   - T0: `web_search` + fetch the top 2–3 results; extract their heading structures and
     which entities/attributes they cover. Note gaps you can beat.
   - T2: `../../scripts/dataforseo_client.py` live SERP + People-Also-Ask for cleaner
     data. Record provenance.

3. **Build the contextual vector** (the outline). Order per contextual-vectors.md:
   definition/snippet lead → defining attributes → values/how-to → comparisons/related
   → question network → edge cases (macro-micro border with a grouper question). Tag
   each heading `entity:` / `attr:` / `rel:` / `q:`, state `must_cover`, set a
   `word_budget` guideline. Keep ONE macro context and one intent.

4. **Snippet target.** Write the ~40-word extractive answer the lead should win.

5. **Internal links.** Pull `up`/`down`/`lateral` from the node; add descriptive,
   varied anchor suggestions from the target nodes' query networks. Justify laterals
   (named shared attribute at T0; embedding distance at T1).

6. **Lock the facts.** List `locked_facts_refs` (keys the article may state) and an
   explicit `do_not_fabricate` list (specs/stats/prices lacking provenance — pull the
   brand's `_pending_owner_confirmation` items into here).

7. **Intent-conflict check** vs sibling nodes (query-semantics.md): flag any node with
   overlapping query network + same intent. T0 by judgement; T1 via
   `../../scripts/semantic_distance.py`.

8. **Emit** `brands/<slug>/briefs/<node-slug>.md` (a readable brief) and, if the
   pipeline wants structured data, a JSON alongside it validating against
   `../../templates/brief.schema.json`. Set node `status: briefed`.

## Definition of done
- One macro context, one intent; outline follows the contextual vector order.
- Every heading tagged + has must_cover; snippet target written.
- Internal links present with varied anchors; laterals justified.
- do_not_fabricate names the unverified brand facts explicitly.
- Intent-conflict check run; conflicts flagged or "none".

## Grounding ladder
- **T0:** LLM reasoning + web_search SERP glimpse; intent/queries `asserted`.
- **T1:** autocomplete-enriched query coverage, embedding-based conflict check + lateral
  justification, SERP-verified intent.
- **T2:** DataForSEO live SERP + PAA questions folded into the question network.
