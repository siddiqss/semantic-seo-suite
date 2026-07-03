# eav-modeling — Entity, Attribute, Value, Predicate

EAV is the decomposition tool that turns "a topic" into a concrete, generative
structure. It's how the topical map, the headings inside a brief, comparisons, and
programmatic templates all get produced from the same underlying model.

## The four parts

- **Entity** — a real-world thing: a product, concept, place, person, organisation
  (e.g. *espresso machine*, *accounts-payable automation*, *Wānaka*).
- **Attribute** — a property of the entity (e.g. espresso machine → *pressure*,
  *boiler type*, *portafilter size*; AP automation → *touchless rate*, *ERP
  integrations*, *approval workflow*).
- **Value** — the concrete value of an attribute (*9 bar*, *dual boiler*, *58 mm*).
- **Predicate** — the relationship linking entity↔attribute; the semantic edge that
  makes it a statement, not a table row (*has pressure of*, *supports*, *is measured
  in*). Predicates are what let the model express *how* things relate, which is the
  part keyword lists lose.

A filled EAV row reads as a sentence: *espresso machine* —(has pressure of)→ *9 bar*.

## Attribute typing (sets depth and priority)

Not all attributes deserve equal treatment. Classify each:

- **Defining** — attributes without which the entity isn't itself (espresso → pressure,
  extraction; AP automation → invoice capture, approval routing). → pillars / strong
  clusters, deep coverage.
- **Unique** — attributes that distinguish this entity/brand from near-neighbours
  (a differentiator). → high-value clusters, often close to monetization.
- **Rare** — attributes that matter to a narrow but real slice of users (edge cases,
  advanced configs). → supporting pages; good for long-tail + completeness.
- **Common** — attributes shared with many entities, low differentiation (generic
  specs everyone lists). → cover briefly for completeness; don't over-invest.

Typing prevents two opposite failures: burying a defining attribute in a footnote, and
building a whole pillar around a common attribute nobody differentiates on.

## From EAV to content structure

Once the central entity is decomposed:

- **Attributes → headings.** Each covered attribute becomes an H2/H3 in a brief; the
  predicate hints the framing (definition vs comparison vs how-to).
- **Values → the substance under a heading.** Concrete values are what make a page
  useful and extractable — *and* where fabrication risk lives (see below).
- **Attribute pairs → comparisons.** Two entities sharing an attribute with different
  values → a comparison page/section (*single vs dual boiler*).
- **Attribute + entity template → programmatic pages.** Fix the entity type +
  attribute pattern once, vary the entity, generate many structurally-identical pages
  (e.g. *[bean origin] flavour profile*, *[ERP] AP integration guide*). Only do this
  where each generated page can carry *real, distinct* values — never to spin near-empty
  templates.

## The non-negotiable rule: values need provenance

This is the anti-fabrication overlay and the single most important line in this doc.

**An attribute value that is a fact — a number, spec, price, benchmark, date — may
only be stated if it is grounded, and it must carry its provenance.**

- Grounded from a real source → `measured` (with `source`). Example: 9-bar espresso
  standard is common knowledge you can cite; a *brand's* price must come from
  `locked-facts.json`.
- Computed from measured inputs → `derived`.
- No source → you may name the *attribute* ("espresso machines have a boiler type")
  but you may **not** assert a specific *value* as fact. If you must illustrate, mark
  it explicitly as an example, or say the data isn't available.

Why this matters: an LLM decomposing an entity will cheerfully emit "touchless rate:
94%" or "pressure: 9.2 bar, confidence 0.97". Those inventions are exactly what makes
wrapper SEO tools untrustworthy. In this suite they are validator failures. When you
don't have a value, the correct output is the attribute plus an honest gap, not a
plausible-sounding number.

## Wikidata grounding (T1)

At tier T1, resolve the central entity and its neighbours against Wikidata
(`scripts/wikidata_entity.py`) to get canonical typing and a real attribute/claim set
— free, `measured` entity grounding. Use it to sanity-check your decomposition and to
pick up attributes you missed. It won't have niche marketing attributes; combine with
domain judgement (labeled `asserted`).

## Worked example A — espresso machine (EAV extract)

| Entity | Predicate | Attribute | Attribute type | Value | Provenance |
|---|---|---|---|---|---|
| espresso machine | operates at | pressure | defining | 9 bar (standard) | measured (common knowledge, citeable) |
| espresso machine | has | boiler type | unique | single / dual / heat-exchange | measured (citeable) |
| espresso machine | uses | portafilter size | common | 58 mm (typical) | measured (citeable) |
| [BrandX] machine | is priced at | price | unique | — | must come from locked-facts.json |

## Worked example B — AP automation (EAV extract)

| Entity | Predicate | Attribute | Attribute type | Value | Provenance |
|---|---|---|---|---|---|
| AP automation | captures via | invoice capture | defining | OCR / e-invoice / EDI | measured (citeable) |
| AP automation | routes via | approval workflow | defining | rules-based / hierarchy | asserted (design description) |
| AP automation | integrates with | ERP integrations | unique | [list] | measured only if verified |
| [OurProduct] | achieves | touchless rate | unique | — | locked-facts.json only; never invent |

## How skills use this doc

- `seo-brand-foundation` builds the brand's own EAV attribute inventory.
- `topical-map-builder` decomposes the central entity via EAV to generate the raw map.
- `content-brief-generator` turns a node's entity + attributes into tagged headings.
- `linking-and-schema` uses entity/attribute relationships for lateral links + schema.
- `validate_draft.py` enforces the value-provenance rule at draft time.
