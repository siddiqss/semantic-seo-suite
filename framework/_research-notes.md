# Framework research notes

Distilled from primary and secondary sources on Koray Tuğberk Gübür's semantic-SEO
methodology ("Koray's Framework" / Holistic SEO / Topical Authority). These notes
are the source of truth for the `framework/*.md` docs. Concepts are tagged:
**[demonstrated]** = supported by published case studies / widely corroborated;
**[theorized]** = plausible mechanism claimed by the framework, not independently proven;
**[our-synthesis]** = our own operationalisation, not from Koray.

Treat "Koray-compliant" throughout the suite as *"follows this methodology"*, never as
*"a documented Google ranking spec."* Google has never published these mechanics; the
framework is a practitioner model with a strong case-study track record.

## Sources consulted
- Koray, "Topical Authority" case study — holisticseo.digital/theoretical-seo/topical-authority (concept origin, 18 May 2022; 0→128k organic traffic in 123 days claim)
- Koray, "3 Suggestions about Topical Authority" — medium.com/@ktgubur (Source-Context ↔ PageRank; "Links in Semantics")
- Koray, "Koray's Agents" — medium.com/@ktgubur (query length distribution → contextual vector breadth; map ≠ keyword list)
- topicalauthority.digital — Topical Authority = Topical Coverage + Historical Data + Cost of Retrieval; EAV + predicates; core/outer sections
- rokonz.com semantic SEO glossary (60+ terms; macro/micro border, contextual connection, "go wider/deeper/faster")
- rankinghacks.com — 5 fundamentals, token insertion, raw vs processed maps, macro-context must return to central entity
- seoconsultant.co / genghisdigital.com.au / pos1.ar — framework overviews; "41 content rules", one-macro-context-per-page, question H2s + ~40-word extractive answers, no-fluff, hub-and-spoke linking, EAV
- thatware.co micro-semantics guide — contextual vector = subtopics; competitor-terms → verbalized entities/questions workflow
- Corroborating 2026 semantic-SEO landscape: ahrefs.com/blog/topical-authority (embedding centroid method), searchatlas, babylovegrowth

## The five fundamentals [demonstrated as the framework's spine]
1. **Source Context** — why the brand deserves to be in the SERP + how it monetizes. The website-entity (site, CEO, socials, brand collateral). Must connect to the central entity via a proper attribute.
2. **Central Entity** — the one entity that appears across every section of the site.
3. **Central Search Intent** — source context + central entity unified; the single intent the site exists to satisfy.
4. **Core Section** — main attributes of the central entity, densified per source context. Where ranking signals concentrate and monetization happens.
5. **Outer Section** — minor/peripheral attributes. Source of *historical data* and trust/quality-signal propagation that earns engine trust; feeds PageRank + relevance into the core.

Solo/small publisher: use the 80/20 version, not full agency-scale. [demonstrated advice]

## Topical Authority formula [framework definition]
Topical Authority ≈ **Topical Coverage × Historical Data × (low) Cost of Retrieval**.
- *Topical Coverage* — completeness across the topic's entities/attributes/queries.
- *Historical Data* — consistent, sustained publishing + performance signals over time. [theorized mechanism]
- *Cost of Retrieval* — how cheaply a search engine can retrieve/understand/serve your content. Clear structure, extractive answers, and schema lower it. [theorized]

## EAV + predicates [demonstrated as core modeling tool]
- **Entity–Attribute–Value** decomposition of the central entity and its neighbours.
- **Predicate** = the relationship/verb linking entity↔attribute (adds the semantic edge).
- Attributes vary by *type*: defining / unique / rare / common — used to decide depth and to spawn headings, comparisons, and programmatic templates. [our-synthesis of attribute typing]
- Rule: values that are facts (specs, numbers, prices) must be grounded, never invented. [our-synthesis — the anti-fabrication overlay; not Koray's emphasis but essential for LLM execution]

## Macro vs micro context [demonstrated]
- **Macro context** = the single overarching topic/intent of a page. *One macro context per page.* The macro context must always bring focus back to the central entity + central search intent.
- **Micro context / microsemantics** = sentence- and section-level relevance signals: co-occurring terms, entity mentions, phrase patterns that build precise context (e.g. "battery lifespan" → "charging cycles", "lithium-ion", "thermal management").
- **Macro–micro border** = the transition zone on a page from main content to supplementary content; provides a slow hand-off and a "grouper question" that deepens the main context while connecting to side topics.

## Contextual vector & information hierarchy [demonstrated]
- **Contextual vector** = the ordered set of subtopics/headings that carry a page's meaning. Headings (H1–H4) are written *as* contextual vectors — each has an explicit semantic role.
- Order of information changes interpretation; heading format/word choice/hierarchy changes context priority.
- Query **length distribution** informs how broad/long the contextual vector should be.
- Typical brief = contextual vector (subtopics) + heading levels + article methodology + query terms. [thatware/topicalmap.services]

## Query semantics [demonstrated]
- Bridge the gap between *query vocabulary* (how users search) and *document vocabulary* (how the page is written).
- Build **query networks** per node: representative queries + variations + question formats (what/why/how/vs/best/near-me).
- Classify **search intent** and align one intent per URL to prevent cannibalization at planning time.

## Selected authorship rules (the "≈41 rules") [demonstrated as the framework's writing style]
- One macro context per page.
- Question-style H2s answered with a concise ~40-word extractive answer near the top (snippet/AEO target).
- Definition-first: lead with what the thing is.
- No fluff — every sentence must carry semantic value; declarative modality; avoid hedging.
- Complete EAV coverage for the page's entity.
- Hub-and-spoke internal linking with descriptive (non-exact-match-spam) anchors.
- Consistency of information across nodes creates "contextual connection" even without a link; a hyperlink strengthens it.
- Content audit / refresh roughly every 6 months.

## Raw vs processed topical map [demonstrated]
- **Raw map** = full brainstormed inventory of every topic/attribute/query (via token/attribute insertion).
- **Processed map** = the raw map filtered, ordered, deduped, tiered, and assigned intent + priority — the version you actually execute.

## Links-in-semantics [theorized, Koray-specific]
- Not "links vs semantics" — links operate *within* the semantic structure. PageRank from a topically-aligned high-authority source helps; from an irrelevant source it doesn't move you toward your central query networks.

## What we deliberately add on top [our-synthesis]
- **Provenance labels** on every value (measured/derived/asserted) — Koray assumes a human with data; an LLM must mark where numbers came from.
- **locked-facts.json** ledger + draft validator — port of a product attribute-lock to stop the model inventing brand specs.
- **Grounding tiers (T0/T1/T2)** — Koray's method is data-hungry; we let it run at zero cost (pure LLM) and improve with free sources or paid APIs, labeling the trust level honestly at each tier.
