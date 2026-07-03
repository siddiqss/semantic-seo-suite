# eeat-signals — Experience, Expertise, Authoritativeness, Trust

E-E-A-T is not a single ranking dial; it's the bundle of signals that make content
credible enough to rank for high-stakes queries. This doc governs the author/org layer
in `linking-and-schema` and the first-hand-experience guidance in
`semantic-writing-rules.md`. The overriding rule: **signals must be real. Never
fabricate credentials, authorship, reviews, or experience.**

## The four, made concrete
- **Experience** — first-hand use/observation. Shows up as specific, lived detail a
  non-practitioner couldn't invent ("after pulling ~40 shots on a dual-boiler, the
  sourness went away once I dropped the grind two clicks"). This is the cheapest,
  strongest differentiator vs generic AI content — *if it's true*.
- **Expertise** — demonstrated subject knowledge: correct terminology, edge cases,
  knowing what's contested. Comes from the content itself + author credentials.
- **Authoritativeness** — being recognised as a source: author entities, an About/org
  page, citations from others, consistent identity across the web.
- **Trust** — the umbrella: accurate claims, transparent sourcing, honest limitations,
  clear ownership. Fabrication destroys it fastest.

## What to build (real signals only)
- **Author entity** — a real person with a bio, credentials, and ideally an external
  footprint. Emit `Person` schema only when a genuine author exists (schema-jsonld.md).
  Do not invent an author to satisfy a template.
- **Organization entity** — About page + `Organization` schema from the entity profile
  (name, url, what the brand is). This is almost always emittable and low-risk.
- **Credential / About pages** — where real qualifications, experience, and the source
  context live. These are legitimate outer-section nodes.
- **First-hand markers in content** — concrete specifics, original data, screenshots,
  results. Prompt the writer to surface real experience the brand has; never manufacture
  it.

## What NOT to do (the wrapper-tool tells)
- No invented testimonials, star ratings, or "trusted by" logos.
- No fabricated case-study numbers ("+312% traffic").
- No fake author personas or borrowed credentials.
- No `Review`/`AggregateRating` schema without real, verifiable reviews.

## For the auditor
Missing org schema, no author on YMYL-ish content, and an About page absent from the
map are legitimate E-E-A-T findings — reported as gaps, not scored with invented numbers.
