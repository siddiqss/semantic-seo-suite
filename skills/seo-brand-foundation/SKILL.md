---
name: seo-brand-foundation
description: >
  Establish or update a brand's semantic-SEO foundation — central entity, source
  context, audience, competitors, EAV attribute inventory, and the locked-facts
  ledger. Use this whenever the user starts SEO work for a new brand or domain, says
  "onboard this brand", "set up SEO for X", "build the entity profile", mentions
  source context or central entity, or asks for a topical map / content plan for a
  brand that has no entity-profile.json yet. Always run this before topical-map-builder
  if the brand's foundation is missing. Triggers even when the user only says "let's do
  SEO for a domain" without naming this step.
---

# seo-brand-foundation

Produce a rigorous, provenance-tagged foundation that everything downstream depends
on. Getting the central entity and core/outer boundary right here is worth more than
any later cleverness — a perfect map of the wrong site is still wrong.

Read `../../framework/source-context.md` and `../../framework/eav-modeling.md` before
starting. Read `../../framework/00-overview.md` if you haven't this session (it sets
the provenance rules you must follow).

## Inputs
- Brand domain + niche (from the user).
- `brands/<slug>/config.yaml` — read it first for grounding tier and sources.

## Workflow

1. **Load config.** Determine tier. Everything below adapts to what's enabled.

2. **Understand the current site (if it exists).**
   - T1 (`crawl: true`): run `../../scripts/crawl_sitemap.py` then
     `../../scripts/extract_page_content.py` on home, about, product/pricing, and the
     top few content pages to infer what the site *currently claims to be*. Record as
     `measured` (crawl).
   - T0: `web_search` the brand + fetch the homepage to infer the same, labeled
     `asserted` where you're inferring.

3. **Resolve the central entity.**
   - Distinguish it from the brand name — it's *what the brand is about* (see
     source-context.md "brand-as-central-entity" failure mode).
   - T1 (`wikidata: true`): `../../scripts/wikidata_entity.py` to get canonical typing
     + a real attribute set (`measured`). T0: type it by judgement (`asserted`).

4. **Write source context + central intent.** What the brand is, who for, how it
   monetizes, and the one intent it exists to satisfy. Derive the **core/outer
   boundary** from monetization (source-context.md). If you can't cleanly classify a
   topic as core or outer later, the boundary here is under-specified — fix it now.

5. **Personas + competitor entities.** 2–4 personas (needs, sophistication).
   Competitors via `web_search` (T0) or domain-competitor data (T2), each tagged.

6. **Brand EAV attribute inventory.** Decompose the brand's own offering into
   attributes (defining/unique/rare/common) per eav-modeling.md. Factual values here
   must be grounded — see step 7.

7. **Seed locked-facts.json.** For every concrete brand fact (price, spec, capability,
   stat) you'd want articles to state: confirm it with the user or a cited source, then
   write it to `brands/<slug>/locked-facts.json` with `source` + `verified_date`. If a
   fact isn't confirmed, it does NOT go in — and articles won't be allowed to state it.
   **Ask the user to confirm brand facts; never invent them to fill the ledger.**

8. **Emit artifacts.**
   - `brands/<slug>/entity-profile.json` — must validate against
     `../../templates/entity-profile.schema.json`; every factual field
     provenance-tagged (use `../../scripts/provenance.py`).
   - `brands/<slug>/locked-facts.json` — must validate against its schema.
   - Append a one-page human-readable foundation summary to the workspace
     (`brands/<slug>/foundation-summary.md`).

## Interview, don't assume
When information is missing (monetization details, what they refuse to cover,
unverified specs), ask the user rather than guessing. The will-not-cover list and the
monetization model are the two answers that most shape the map — get them explicitly.

## Definition of done
- entity-profile.json validates; central entity is the subject, not the brand name.
- Core/outer boundary is stated as a rule you could apply to a new topic.
- locked-facts.json exists (may be small) with sources on every fact.
- No bare numbers anywhere: run `provenance.audit()` mentally / via the validator.

## Grounding ladder
- **T0:** LLM + web_search; most fields `asserted`; entity typed by judgement.
- **T1:** + Wikidata typing (`measured`) + site crawl of claimed identity (`measured`).
- **T2:** + DataForSEO domain-competitor data for the competitor list (`measured`).
