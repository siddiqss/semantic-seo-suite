# source-context — the root that constrains everything

Before a single topic is chosen, you fix *what the brand is* and *why it deserves to
rank*. Get this wrong and the whole map inherits the error: you'll produce a
technically-complete topical map for the wrong site. This doc defines the five
fundamentals and how they set the boundary of what the brand may cover.

## The five fundamentals

1. **Source context** — *why this brand belongs in the SERP, and how it makes money.*
   It includes the whole web-entity: the site, its founder/CEO, social profiles, and
   brand collateral. Source context must connect to the central entity through a real
   attribute. It answers: what is this business, who is it for, and how does a search
   visitor become a customer?

2. **Central entity** — the single entity present across every section of the site.
   Everything on the site is, ultimately, about this. It is usually the product
   category, service, or subject the brand is built on — not the brand name itself.

3. **Central search intent** — source context **+** central entity, unified into the
   one intent the site exists to satisfy. It is the north star every page bends back
   toward.

4. **Core section** — the topics covering the *main* attributes of the central entity,
   densified around the source context. This is where ranking signals concentrate and
   where monetization happens (money pages + the content closest to them).

5. **Outer section** — topics covering *minor/peripheral* attributes. These earn trust
   and accumulate historical data, and they pass relevance + PageRank inward to the
   core. Authority feeders, not money pages.

> Mnemonic: **source context** is the *why*, **central entity** is the *what*,
> **central intent** is the *why + what fused*, **core** is where you *earn*, **outer**
> is where you *build trust that flows to core*.

## Deriving the core/outer boundary from monetization

The boundary is not aesthetic — it's economic. Draw it like this:

- A topic is **core** if covering it plausibly moves a reader toward the brand's
  monetization within one or two steps (comparison, decision, how-to that leads to the
  product, use-case that the product solves).
- A topic is **outer** if it builds subject credibility and captures top-of-funnel or
  adjacent interest but doesn't route to money directly. It exists to (a) complete the
  topic so the engine sees full coverage and (b) funnel authority to the core.

If you can't say which side a topic is on, you haven't finished the source context.
Ambiguity here is the tell that the brand's monetization model is under-specified.

## The "right to cover" test

A brand should only expand into topics its source context earns. A coffee-equipment
store writing about "morning productivity routines" is a classic dilution error — the
topic is loosely associated but the brand has no credible reason to own it, and it
pulls the site's topical centre away from coffee. Ask of every candidate outer topic:

1. Does the central entity connect to it by a *real* attribute (not a vibe)?
2. Would covering it confuse an engine about what the site is for?
3. Does the brand have genuine standing/experience to cover it well?

Two "no"s → drop it. This test is what separates a focused authority site from a
content farm, and it's the discipline wrapper tools skip.

## Worked example A — specialty coffee retailer

- **Source context:** an online store selling specialty beans + home brewing gear;
  monetizes via product sales and a subscription; founder is a certified Q-grader.
- **Central entity:** *specialty coffee* (subsuming beans, brewing, equipment).
- **Central search intent:** help home enthusiasts choose, buy, and brew better
  specialty coffee → convert to purchase/subscription.
- **Core section:** brewing methods that use gear they sell, bean selection/buying
  guides, grind/dose/ratio how-tos, equipment comparisons, subscription value.
- **Outer section:** coffee history, origin/terroir explainers, caffeine science,
  café-business basics — credibility + top-of-funnel, linking down to core.
- **Will-not-cover:** general productivity, unrelated kitchen appliances, diet fads.

## Worked example B — B2B SaaS (invoice-automation product)

- **Source context:** SaaS that automates accounts-payable invoice processing for
  mid-market finance teams; monetizes via seat-based subscription; team has AP domain
  expertise.
- **Central entity:** *accounts-payable / invoice automation*.
- **Central search intent:** help AP and finance leaders understand, evaluate, and
  adopt touchless invoice processing → convert to trial/demo.
- **Core section:** invoice-processing workflows, AP automation ROI, integration
  guides (ERPs), evaluation/comparison content, migration guides.
- **Outer section:** broader finance-ops topics (month-end close, AP vs AR, fraud
  controls, e-invoicing regulations) — authority + adjacent demand feeding core.
- **Will-not-cover:** generic "productivity", unrelated HR/payroll, personal finance.

## What the foundation must output

The `seo-brand-foundation` skill turns this doc into `entity-profile.json`:
central entity (+ type, Wikidata QID if resolvable at T1), source context (what /
audience / monetization / will-not-cover), central intent, the core/outer boundary
definition, personas, competitor entities, and the brand's own EAV attribute
inventory. Every factual field is provenance-tagged; confirmed brand facts are also
written to `locked-facts.json`.

## Common failure modes

- **Brand-as-central-entity.** "Acme" is not the central entity; *what Acme sells/does*
  is. The brand is part of source context.
- **Outer section with no core to feed.** Lots of top-of-funnel explainers, no money
  pages — authority with nowhere to flow. Define core first.
- **Boundary drawn by search volume instead of monetization.** High-volume adjacent
  topics tempt you off-centre. Volume informs *priority within* the allowed set, never
  whether a topic is allowed.
