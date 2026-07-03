---
name: semantic-draft-writer
description: >
  Write a full article draft from a semantic-SEO brief, following the micro-semantics
  writing rules and the brand's locked facts, then validate-and-repair it against the
  fabrication guard. Use whenever the user says "write the article", "draft from this
  brief", "turn this node into content", or asks to produce the actual copy for a
  topical-map node. Always runs scripts/validate_draft.py and repairs violations before
  returning. Triggers on drafting/writing intent for mapped content.
---

# semantic-draft-writer

Turn a brief into publishable copy that is deep, specific, extractive, and — the part
other tools skip — factually honest. "Passes the validator" is the floor, not the goal:
the goal is a piece genuinely worth reading. The draft is done when it is fabrication-clean
AND clears the quality bar (or its remaining gaps are explicitly surfaced).

Read first: `../../framework/semantic-writing-rules.md` (especially the **Craft & depth
rules 22–28**), `../../framework/macro-micro-semantics.md`. Load the brief, the node,
`brands/<slug>/locked-facts.json`, and `entity-profile.json` (for voice/audience).

## Workflow

0. **Scope depth and surface fact gaps FIRST.** Before writing, list the concrete
   specifics a strong piece needs — real examples, named entities, figures, a point of
   view — and check them against `locked-facts.json` + the brief. If the piece can only be
   written generically because the facts aren't there, that is a signal to **ask the user
   for the missing specifics** (real customer result, actual feature names, a workflow
   detail) rather than writing vague filler. Thin facts are the #1 cause of thin drafts.

1. **Front-matter first.** Emit the required block (semantic-writing-rules.md): node_id,
   target_query, intent, entities_covered, internal_links, schema_type,
   locked_facts_used (start empty), sources (start empty).

2. **Draft for a reader, section by section along the brief's contextual vector.** Lead a
   section with the extractive answer (rules 3–4) THEN go deep: mechanism, a concrete
   example (rule 23), a trade-off, a real point of view (rule 26). Do not turn every H2
   into a tiny Q&A (rule 27) — vary the shape. Declarative, specific, filler-free.

3. **Honour the locks while writing:**
   - State a brand fact ONLY if it exists in `locked-facts.json`; when you use one, add
     its key to `locked_facts_used`.
   - State an external factual number ONLY with a citation; add the URL to `sources`.
   - Where a figure would help but isn't grounded, write the honest version (mechanism/
     range/"depends on…") — never invent one. Pull from the brief's `do_not_fabricate`.

4. **Insert internal links** from the brief with varied, descriptive anchors
   (internal-linking-rules.md).

5. **Editorial self-critique pass (before the gates).** Re-read the draft as a skeptical
   editor: Which section is thin? Where is there no example? What's the non-obvious point,
   and is it actually there? Cut every filler sentence. Rewrite the weakest section. Do
   this once *before* running the scorers — the gates confirm quality, they don't create it.

6. **Three-gate loop — fabrication is a hard gate; quality is the target; AEO is a floor:**
   ```
   # (a) HARD GATE — must be 0 high, or surface remaining violations
   python ../../scripts/validate_draft.py --draft <draft.md> \
     --locked brands/<slug>/locked-facts.json --brief brands/<slug>/briefs/<slug>.json \
     --brand-terms "<Brand>" --json
   # (b) QUALITY — the number to optimize (target >= 80)
   python ../../scripts/draft_quality.py --draft <draft.md> --floor <800+ per node type> --json
   # (c) AEO — a FLOOR to clear (target >= 80), NOT a number to maximize
   python ../../scripts/aeo_score.py --draft <draft.md> --schema-dir brands/<slug>/data/schema --json
   ```
   Repair in priority order: fabrication first (never fix a fabrication by inventing a
   source — tell the truth or cut the claim); then work the `draft_quality.py` fixes
   (deepen shallow sections, add the missing examples, cut filler, reach length through
   depth); then confirm AEO ≥ ~80. **Do not sacrifice depth to push AEO past ~85** — a
   formulaic all-Q&A page is the failure mode this loop exists to prevent. Repeat ~2–4×.

7. **Surface, don't hide.** If violations or an unavoidable quality gap remain (e.g. the
   piece stays generic because a brand fact the user hasn't confirmed is missing), STOP
   and list them with the exact sentences and the specific facts you need — rather than
   shipping filler or faking a source. These usually map to `_pending_owner_confirmation`.

8. **Emit** `brands/<slug>/drafts/<node-slug>.md`; set node `status: drafted`.

## Definition of done
- `validate_draft.py`: 0 high-severity violations (or remaining ones surfaced with rationale).
- `draft_quality.py`: **>= 80** — every section has depth and a concrete example; filler
  is gone; length reached through substance. This is the bar the writer is judged on.
- `aeo_score.py`: **>= 80** (floor cleared; not maximized at the cost of depth).
- Front-matter accurate; reads as a genuine expert with a point of view, not a padded FAQ.

## Grounding ladder
- **T0:** research external facts via web_search (cite them); brand facts from locked
  ledger only.
- **T1+:** same rules; richer sourcing. Grounding tier never relaxes the fabrication
  guard — it only changes where legitimate numbers come from.
