# schema-jsonld — structured data per node type

JSON-LD lowers a page's cost of retrieval by handing the engine an explicit, machine-
readable statement of what the page is. `linking-and-schema` (via
`scripts/schema_jsonld.py`) emits it from the map + entity profile. The hard rule
carries over: **schema states only grounded facts** — no invented prices, ratings, or
reviews.

## Node → type mapping
- **HowTo** — procedural nodes ("how to …", step-based). Emit `HowTo` with `step`s from
  the query network / brief.
- **FAQPage** — question-shaped nodes, or any node with a strong question network. Emit
  `FAQPage` with `Question`/`Answer` pairs (answers pulled from the draft, not invented).
- **Product** — core commercial/transactional nodes about the offering. Emit `Product`;
  add an `Offer` **only** if a price exists in `locked-facts.json` — otherwise omit the
  Offer and note why. Never attach `AggregateRating` without real reviews.
- **Article** — everything else (informational/outer). Emit `Article` with `about` =
  the node's entities.

## Site-level graph
Emit one `Organization` node from the entity profile (name, url, description) on every
page or in a shared graph. Add a `Person` (author) node **only** when a real author with
credentials exists (eeat-signals.md). `BreadcrumbList` can mirror the pillar→cluster→
supporting path for navigational clarity.

## Fact discipline in schema
Schema is a favourite place for fabrication to hide because it's not read by humans.
The generator therefore:
- pulls `Offer.price` only from a locked price fact (with its `_source`);
- never emits ratings/review counts unless supplied from real data;
- leaves answer text as a placeholder to be filled from the validated draft, so no
  invented answer ships in markup.

## Validation
`schema_jsonld.py` checks each block is JSON-serialisable and has `@context`/`@type`,
and writes a per-node checklist. For production, additionally run Google's Rich Results
Test / schema.org validator before publishing — syntactic validity here is necessary,
not sufficient.
