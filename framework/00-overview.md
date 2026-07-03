# 00 — Overview: the mental model

This knowledge base is the reasoning core of the Semantic SEO Suite. Skills stay
thin and point here. Read this first; it tells you how the pieces fit and which
doc to open next.

## The one-paragraph model

Modern search ranks **entities and topics, not isolated keywords**. A site wins by
demonstrating *topical authority*: near-complete, well-structured coverage of a
topic, published consistently over time, in a form that is cheap for a search
engine (and now an LLM answer engine) to retrieve and trust. You build it by
defining what the brand *is* (its central entity and source context), mapping the
full topic space around it (a topical map of pillars → clusters → supporting
pages), and writing each page as a tightly-ordered answer to one intent (macro
context) reinforced by precise sentence-level signals (microsemantics).

Everything else in this suite is machinery for doing that reliably and without
fabricating data.

## The authority equation

Topical Authority ≈ **Topical Coverage × Historical Data × low Cost of Retrieval**

- **Coverage** — did you cover the topic's entities, attributes, and query network
  completely? (Built by `topical-map-builder`, checked by `semantic-site-auditor`.)
- **Historical Data** — are you publishing consistently and accumulating real
  performance signals over time? (Tracked by `seo-performance-tracker`.)
- **Cost of Retrieval** — is your content structured so an engine can extract the
  answer cheaply? Clear hierarchy, extractive answers, schema. (Enforced by
  `content-brief-generator`, `semantic-draft-writer`, `linking-and-schema`.)

This is a practitioner model with a strong case-study record, **not** a published
Google spec. Write and speak accordingly: "this methodology holds that…", never
"Google requires…". See `_research-notes.md` for what is demonstrated vs. theorized.

## When this methodology is worth it — and when it's overkill

Worth the full treatment: content-driven growth in a definable niche, a brand that
can credibly own a topic, competitive SERPs where thin content won't rank, and
sites publishing enough volume for historical-data effects to matter.

Overkill / adapt down: a five-page brochure site, a purely transactional store with
no content ambition, or a brand with no genuine claim to the topic. In those cases
run the "80/20" version — foundation + a small core-section map — and skip the
outer-section sprawl. Don't manufacture authority a brand hasn't earned; that's how
you get generic filler that fools no one (the exact failure of wrapper SEO tools).

## The non-negotiable overlay: provenance & no fabrication

Koray's method assumes a human analyst holding real data. An LLM will happily invent
a "search volume: 1,300" or "confidence: 0.97". This suite forbids that structurally:

- Every factual value carries a provenance tag — `measured`, `derived`, or
  `asserted` (see `scripts/provenance.py`). A bare number is a bug.
- Brand claims (prices, specs, stats) may only be stated if they exist in the
  brand's `locked-facts.json`; the draft validator rejects the rest.
- When a grounding source isn't configured, skills **degrade and label**, they do
  not guess numbers. "Intent: informational (asserted — no SERP data)" is correct;
  "Volume: 1,300" with no source is not.

If you ever feel the urge to make the output look more data-driven than it is, that
urge is the signal to add a provenance tag, not a number.

## Grounding tiers

Every capability runs at three levels, chosen per brand in `config.yaml`:

- **T0 — pure LLM** + `web_search`/`web_fetch`. Zero setup. Map structure, briefs,
  drafts. Most values are `asserted`.
- **T1 — free sources** — Google Autocomplete, Wikidata, Trends, local embeddings,
  site crawl, Google Search Console. Upgrades many values to `measured`/`derived`.
- **T2 — paid** — live SERP data. SerpApi (current provider: measured SERP signals —
  PAA/related breadth, incumbent authority, ad count) or DataForSEO (search volume +
  difficulty, if a working account exists). Both feed `reprioritize_map.py`.

Tiers are mixable. A skill never fails for lack of a tier; it does the best
available version and labels provenance.

## Document map

Foundation & structure:
- `source-context.md` — central entity, source context, central intent, core/outer split.
- `topical-map-theory.md` — pillar/cluster/supporting, raw vs processed map, coverage depth.
- `eav-modeling.md` — Entity–Attribute–Value + predicates; attribute typing.
- `query-semantics.md` — query networks, intent classification, query↔document vocabulary.

Page-level craft:
- `contextual-vectors.md` — heading order as meaning; macro-micro border; split vs merge.
- `macro-micro-semantics.md` — one macro context per page; sentence-level signals.
- `semantic-writing-rules.md` — the authorship rulebook + anti-fabrication in prose.

Connective tissue & signals:
- `internal-linking-rules.md` — hub-and-spoke, up/down/lateral, anchors, orphans.
- `eeat-signals.md` — author/org entities, credentials, first-hand experience.
- `schema-jsonld.md` — structured data per node type.

Visibility & distribution (beyond the ranked link):
- `answer-engine-optimization.md` — AEO/GEO: making mapped content citable by AI answer
  engines (Google AI Overviews, ChatGPT, Perplexity), measured honestly.
- `off-page-authority.md` — link-opportunity plays, safe off-page anchor mix, competitor
  backlink-gap; provenance on every prospect, nothing fabricated.
- `content-distribution.md` — per-piece channel fit, repurposing atoms, promotion cadence;
  channels matched to real personas, no invented reach numbers.

Each doc carries its own examples in two unlike niches (specialty coffee and B2B
SaaS) so the reasoning generalises beyond any single brand.
