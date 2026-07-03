# semantic-writing-rules — the authorship rulebook

The rules `semantic-draft-writer` follows and `validate_draft.py` enforces. These
operationalise the framework's authorship guidance (the "≈41 rules") plus the suite's
non-negotiable anti-fabrication overlay. Read `macro-micro-semantics.md` and
`contextual-vectors.md` first; this doc is the applied checklist.

## Structure rules
1. **One macro context per page.** One topic, one intent, one primary entity.
2. **Follow the brief's contextual vector.** Heading order and roles come from the brief;
   don't reorder or invent sections that break the vector.
3. **Definition/answer first.** Lead the page and each section with the answer, then
   elaborate. Snippet target sentence sits at the very top.
4. **Question H2s get ~40-word extractive answers** immediately beneath them.
5. **Hierarchy by importance.** Defining attributes deep and prominent; common ones brief.

## Sentence rules
6. **Declarative modality.** State plainly; avoid hedging except for genuine uncertainty.
7. **No fluff.** Every sentence carries semantic value. No throat-clearing, no restating
   the heading, no empty transitions ("Now let's dive in").
8. **Definition-first sentences** open sections.
9. **Entity prominence.** Name entities; don't over-rely on pronouns.
10. **Natural co-occurrence, never stuffing.** Include expert-adjacent terms only where
    a real sentence needs them. Keyword density is an output, not a target.
11. **Consistency.** State shared facts identically across the site's pages.

## Evidence & fabrication rules (the hard line)
12. **No naked factual values.** Any number, %, price, spec, date, or benchmark must be
    grounded. Two legitimate sources:
    - a cited external source → `measured`, with the citation in front-matter;
    - the brand's `locked-facts.json` → for brand claims only.
    Anything else: state the mechanism/relationship without the figure, or mark an
    explicit illustrative example.
13. **Brand claims are locked.** The draft may state a fact about the brand/product only
    if a matching entry exists in `locked-facts.json`. No price, no "up to X%", no
    feature that isn't confirmed. This is a product-attribute lock, generalised.
14. **External facts must be cited.** If the writer researches a live source for a stat,
    the source goes in the draft's front-matter `sources` list. Uncited external stats
    are violations.
15. **Graceful "no data."** When a figure would help but isn't available, write the
    honest version rather than inventing one. "Cost per invoice varies by volume and
    complexity" is correct; "cost per invoice is $2.36" without a source is a violation.
16. **No fabricated authority signals.** Don't invent testimonials, review counts,
    "trusted by" logos, case-study results, or precision like "confidence: 0.97". (These
    are exactly the tells of wrapper SEO tools; the suite exists partly to avoid them.)

## Linking & schema rules
17. **Insert the brief's internal links** with descriptive, varied anchors (not
    exact-match repetition). Up-links to parent, down-links to children, justified
    laterals only. (internal-linking-rules.md)
18. **Emit the intended schema type** in front-matter so `linking-and-schema` can render
    JSON-LD (Article/FAQ/HowTo/Product per node).

## E-E-A-T rules
19. **First-hand experience where real.** Prefer concrete, specific, experience-grounded
    detail over generic advice — but never fabricate experience the brand doesn't have.
20. **Attribute expertise honestly.** Author/organisation signals come from real
    credentials (eeat-signals.md), not invented ones.

## Craft & depth rules (quality, not just safety — enforced by draft_quality.py)
Rules 1–20 keep a draft honest and extractable. They do not make it *good*. A draft that
passes the fabrication guard and scores AEO 100 can still be thin, generic FAQ filler.
These rules raise the floor from "safe" to "worth reading", and `scripts/draft_quality.py`
scores them (DEPTH, EXAMPLES, SPECIFIC, ANTIFLUFF, LENGTH).

22. **Depth over coverage.** Each H2 section earns its place — aim for ~90+ words of real
    substance (mechanism, trade-off, consequence), not a one-line answer and move on.
    Answering a question is the start of a section, not the whole of it.
23. **One concrete example per major section.** Show, don't just assert: a named scenario
    ("a Shopify supplement brand testing five hooks…"), a specific tool/model, a worked
    case. Generic advice with no example is the #1 quality failure.
24. **Specificity beats abstraction.** Name real entities (Kling, Meta, Nano Banana 2, a
    real competitor behaviour), use grounded figures, reference concrete mechanics. Vague
    nouns ("solutions", "content", "workflows") signal thin thinking.
25. **Kill filler.** No "leverage/utilize/robust/seamless/cutting-edge/it varies/depends
    on many factors/when it comes to." If a sentence survives deletion with no meaning
    lost, delete it.
26. **A point of view.** Say something non-obvious the reader can't get from the SERP's
    top result — a real trade-off, a contrarian take grounded in fact, a "most teams get
    this wrong because…". Neutral summary is commodity content.
27. **Vary section shape.** Do NOT turn every H2 into a question + 40-word answer. Use the
    extractive Q&A shape (rules 3–4) for genuinely queryable sections; write the rest as
    real prose with depth. The extractive lead is a *tool for some sections*, not a
    template for all of them.
28. **Substantial length, no padding.** Pillars run long because they go deep, not because
    they repeat. Hit the depth first; length follows. `draft_quality.py --floor` sets the
    target per node type.

> **AEO is a floor, not a target.** `aeo_score.py` ≥ ~80 means the piece is citable —
> stop there. Chasing 100 by making every section a tiny Q&A trades reader value for a
> metric. Optimize `draft_quality.py` (subject to a clean fabrication guard); treat AEO as
> a threshold to clear, not a number to maximize.

## Maintenance
21. **Refresh cadence.** Flag content for review ~every 6 months or when locked-facts
    entries expire; volatile facts (prices) carry an `expires` date.

## Draft front-matter (required)
Every draft begins with a front-matter block the validator reads:

```yaml
---
node_id: n-015
target_query: "ai ad product accuracy"
intent: informational
entities_covered: [product accuracy, attribute fabrication, brand control]
internal_links: {up: [], down: [n-016, n-017, n-018], lateral: []}
schema_type: Article
locked_facts_used: []          # keys from locked-facts.json actually stated
sources:                        # external citations for any measured external fact
  - "hyperfx.ai/blog/best-ai-ugc-tools-for-ads-2026"
---
```

## What the validator checks (see scripts/validate_draft.py)
- Front-matter present and parseable; `node_id` matches a map node.
- Heading structure matches the brief's outline (roles/order preserved).
- No naked factual numbers outside cited/locked contexts.
- Every brand claim traces to a `locked-facts.json` key listed in `locked_facts_used`.
- Every external stat has a `sources` entry.
- Micro-semantics lint: hedge-word density, question→answer adjacency, definition-first
  openings, fluff detection.
Unresolved violations are surfaced to the user — never silently "fixed" by deletion of
the honest gap.
