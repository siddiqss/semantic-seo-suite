---
name: answer-engine-optimizer
description: >
  Optimize a brand's mapped content to get cited by AI answer engines — Google AI
  Overviews, ChatGPT, Perplexity, Gemini. Scores drafts for citation-readiness with
  aeo_score.py, produces a per-node hardening checklist, and spot-checks live AI answers
  for whether the brand (vs competitors) is cited. Use whenever the user mentions AEO,
  GEO, LLM SEO, "getting cited by ChatGPT/Perplexity", AI Overviews, answer engines, AI
  search visibility, or asks why an AI assistant recommends competitors and not them.
  The GEO half of seo-performance-tracker. Never invents a visibility score. Triggers on
  AI-visibility / answer-engine intent broadly.
---

# answer-engine-optimizer

The citation feedback loop. Where `seo-performance-tracker` measures Google rankings,
this optimizes for being the *source an LLM quotes* — which, for a tool category whose
buyers research inside ChatGPT and Perplexity, is where a lot of the demand now decides.

It reuses the suite's spine: read the brand workspace, respect the grounding tier, tag
every value, and feed results back into the map and calendar. It layers onto the on-page
map — same nodes, hardened — it does not replace it.

Read first: `../../framework/answer-engine-optimization.md` (the method + the honesty
rules), then `../../framework/macro-micro-semantics.md` (the writing tactics it scores).

## Preconditions
- `entity-profile.json` + `topical-map.json` exist (run seo-brand-foundation /
  topical-map-builder first).
- Drafts to score live in `brands/<slug>/drafts/`. With no drafts yet, the skill still
  produces the hardening spec and the live-answer probe.
- Live-answer probing needs `grounding.sources.web_search: true` (T1). Without it, do the
  offline scoring only and say the probe was skipped — do not guess citations.

## Workflow

1. **Score citation-readiness (T0, offline).** For each draft:
   ```
   python ../../scripts/aeo_score.py --draft brands/<slug>/drafts/<slug>.md \
     --schema-dir brands/<slug>/data/schema --json
   ```
   Run it *after* `validate_draft.py` is clean — AEO is advisory, fabrication is a gate.
   Collect score, grade, and the specific fixes (DEF / QA / TLDR / LIFT / BREV / SELF /
   SCHEMA). Scores are `measured` (mechanical), the recommended rewrites are `asserted`.

2. **Probe live answer engines (T1, web_search).** For the highest-value target queries
   (core-section, especially comparison/alternative nodes), query them answer-style and
   record, per query + engine + date: is the brand named? cited with a link? which
   competitor sources are quoted instead? This is a dated spot check (n=1 per probe),
   labelled `measured` — **not** a rank tracker. Never aggregate it into a visibility %.

3. **Write the AEO report** → `brands/<slug>/audits/<date>-aeo.md`:
   - **Readiness table** — per node: AEO score, grade, top fixes (`measured` + `asserted`).
   - **Live citations** — per probed query: brand cited? competitors cited? (`measured`,
     dated, with the query text; honest about the tiny sample).
   - **Hardening queue** — nodes `<70`, ranked, with the concrete edits.
   - If web_search is off: state the probe was skipped; emit only the readiness table.

4. **Feed the loop.**
   - Nodes scoring `<70` → mark `needs-update` in the map; push up `calendar.md`.
   - Apply hardening to drafts via **semantic-draft-writer**; ensure JSON-LD via
     **linking-and-schema**. Re-score to confirm the lift.
   - Queries where competitors are cited and the brand isn't → a hardening task on the
     owning node and a signal for off-page authority (**link-opportunities**).
   - New questions found while probing → query-network additions via
     **topical-map-builder**.

## Definition of done
- Every existing draft scored; a dated AEO report with the three sections written.
- Hardening queue fed back into map statuses + calendar.
- No invented visibility number anywhere — citations are dated, per-query observations or
  they are absent. If web_search was off, the report says so.

## Grounding ladder
- **T0:** offline `aeo_score.py` readiness scoring + hardening spec. Fully useful alone.
- **T1 (web_search):** + live answer-engine spot checks (`measured`, dated, per query).
- **T2:** no paid dependency; SERP-feature data from DataForSEO (if on) can corroborate
  which queries trigger AI Overviews, labelled `measured`.
