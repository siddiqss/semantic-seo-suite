# query-semantics — query networks, intent, and vocabulary bridging

A topical map node is only as good as the queries it actually satisfies. This doc
covers how to expand a node into its **query network**, classify **intent**, and
bridge the gap between how users *search* and how a page is *written*.

## The core problem: query vocabulary ≠ document vocabulary

Users search in their words ("why is my espresso sour"); pages are often written in
the author's words ("under-extraction and its causes"). Semantic SEO closes that gap
by deliberately covering the query vocabulary — the actual phrasings, questions, and
co-occurring terms — inside content written around the entity. Miss the bridge and you
can have a comprehensive page that ranks for nothing people type.

## Query networks

Each node has a **target query** (its canonical/representative query) plus a **query
network**: the cluster of variations, sub-questions, and related phrasings that belong
to the *same intent*. The query network:

- defines what the page must cover to be complete,
- feeds the heading structure (many sub-questions → H2/H3s),
- supplies varied internal-link anchor text,
- and is the unit compared across nodes to detect cannibalization.

Keep the network tight to *one intent*. Queries that imply a different intent belong to
a different node (see cannibalization, below).

## Question formats to enumerate

For most informational nodes, systematically generate these families around the
entity/attribute:

- **Definitional:** what is X, X meaning, X vs Y (disambiguation).
- **Causal / explanatory:** why does X, how does X work, what causes X.
- **Procedural:** how to X, steps to X, X guide/tutorial.
- **Comparative:** X vs Y, best X for Z, X alternatives.
- **Evaluative / commercial:** best X, X reviews, is X worth it, X pricing.
- **Situational:** X for [persona], X when [condition], X near me (if local).

Not every family applies to every node; pick the ones the intent supports.

## Search intent classification

Assign exactly one primary intent per node/URL:

- **Informational** — user wants to understand/learn. (Most outer + top-of-core.)
- **Commercial** — user is evaluating options pre-purchase (comparisons, "best",
  reviews). (Core, mid-funnel.)
- **Transactional** — user is ready to act (buy, sign up, demo, pricing). (Core, money.)
- **Navigational** — user wants a specific brand/page. (Usually not something you map.)

Intent drives page type, tone, CTA, and schema. One URL serving two intents is the most
common cannibalization + dilution cause.

## Expansion by grounding tier

**T0 (pure LLM + web_search):**
- Generate the query network by reasoning over the entity/attribute + question
  families; validate phrasings and check for obviously different intents by fetching a
  few live results with `web_search`.
- Intent is `asserted` (inferred from query shape and the SERP glimpse).
- No search volumes — do not invent them. Demand is judged qualitatively.

**T1 (free sources):**
- `fetch_autocomplete.py` — expand the target query via Google Suggest (a–z suffixes,
  question prefixes) to harvest real user phrasings → `measured` query variants.
- `fetch_trends.py` — relative interest + related queries for rough, *relative* demand
  (`measured`, but relative not absolute).
- `serp_intent_classifier.py` — classify intent from the composition of a real SERP
  (result types) → upgrades intent from `asserted` to `measured`.
- Embeddings (`cluster_keywords.py`) group the harvested variants and flag overlaps.

**T2 (paid):**
- `dataforseo_client.py` — real absolute search volume, keyword difficulty, live SERP,
  and People-Also-Ask questions → `measured` demand + a richer query network.

At every tier: label provenance, and let the network be smaller-but-honest rather than
padded with invented terms.

## Cannibalization via query overlap

Two nodes whose query networks overlap heavily *and* share an intent will cannibalize.

- **T0:** judge overlap by inspection; if two target queries would return the same
  SERP with the same intent, merge them.
- **T1+:** embed the query networks and compute pairwise similarity; flag sibling pairs
  above `cannibalization_threshold`. Resolve by merging or by re-scoping one node to a
  distinct intent (e.g. split "best espresso machine" [commercial] from "how espresso
  machines work" [informational]).

## Contextual coverage, not keyword stuffing

Covering the query network means the page *addresses* those questions and naturally
includes the co-occurring vocabulary — not that you cram exact-match phrases. Density is
a by-product of genuine coverage. See `macro-micro-semantics.md` for how this shows up
at the sentence level and `semantic-writing-rules.md` for the anti-stuffing rules.

## Worked example — node "sour espresso" (specialty coffee)

- **Target query:** why is my espresso sour
- **Intent:** informational (`asserted` at T0; confirm via SERP at T1)
- **Query network:** sour espresso causes, under-extraction espresso, espresso too
  acidic fix, grind too coarse espresso, sour vs bitter espresso, how to fix sour shot.
- **Question families used:** causal (why/what causes), procedural (how to fix),
  comparative (sour vs bitter).
- **Cannibalization watch:** keep separate from "bitter espresso" (over-extraction) —
  different cause, different intent-detail; link laterally, don't merge.

## Worked example — node "AP automation ROI" (SaaS)

- **Target query:** accounts payable automation ROI
- **Intent:** commercial (evaluators justifying spend)
- **Query network:** AP automation cost savings, invoice processing cost per invoice,
  AP automation payback period, is AP automation worth it, AP automation business case.
- **Grounding note:** any cost-per-invoice or savings figure is `measured` only from a
  cited study or the brand's `locked-facts.json`; otherwise present the model/method,
  not a fabricated number.
