# contextual-vectors — heading order as meaning

A page's meaning isn't just its words — it's the *order and hierarchy* of what it
covers. The **contextual vector** is the ordered set of headings/subtopics that carries
a page's semantics. Two pages with identical facts but different heading order signal
different things to a search engine and read as different-quality answers to a human.
This doc governs how `content-brief-generator` structures a page.

## The contextual vector

Write every heading (H1–H4) *as a contextual vector element* — each has an explicit
semantic role, not just a label. A brief's outline is the contextual vector made
concrete: for each heading you state its role, what it must cover, and which entities
belong to it.

Default ordering for an informational page about an entity:

1. **Definition / what it is** (the lead — also your snippet target).
2. **Defining attributes** (the attributes without which the entity isn't itself).
3. **Values / how-to / mechanics** (the substance; concrete, extractable).
4. **Comparisons & related entities** (X vs Y; neighbours sharing an attribute).
5. **Question network** (the remaining what/why/how the query network demands).
6. **Edge cases / caveats** (narrow but real; the macro→micro border, see below).

Order changes interpretation: leading with a comparison before defining the thing
signals a commercial page; leading with a definition signals informational. Match the
order to the node's intent (query-semantics.md).

## One macro context per page

The single most important structural rule (see macro-micro-semantics.md): a page has
**one** macro context — one topic, one intent. Every heading must bend back toward the
central entity + the page's intent. A heading that pulls toward a *different* intent
belongs on a different page; keeping it here is how cannibalization and dilution start.

The macro context must, at the page level, return focus to the site's central entity —
even outer-section pages should make their connection to the core legible.

## The macro–micro border

Real pages transition from **main content** (the macro context, densely on-topic) to
**supplementary content** (related side-topics, deeper cuts, tangents). That transition
is the **macro–micro border**. Handle it deliberately:

- Provide a *slow* hand-off, not a cliff — a bridging section that stays connected to
  the main context while opening a side door.
- Use a **grouper question** at the border: a question that deepens the main context
  *and* connects to an adjacent topical-map node (e.g. at the end of "sour espresso":
  *"Is bitter espresso the opposite problem?"* → bridges to the bitter-espresso node).
- Everything before the border is what the page ranks on; everything after builds
  connection and internal-link opportunities. Don't let supplementary content outweigh
  the main context.

## Split vs merge (cannibalization at the structural level)

While outlining, you're constantly deciding whether two subtopics are one page or two:

- **Merge** into one page when they share one intent and one macro context (e.g.
  "espresso grind size" + "espresso dose ratio" → both are "dialing in espresso").
- **Split** into two pages when they carry different intents even if lexically close
  (e.g. "how espresso machines work" [informational] vs "best espresso machine"
  [commercial]). Forcing both onto one URL serves neither.

If a heading needs its own intent, its own CTA, or its own snippet answer, it wants to
be its own page. Kick it back to the map as a new node rather than bloating this one.

## Information hierarchy & prominence

- **Heading level** encodes importance: H2 = a major facet of the macro context; H3 =
  a sub-facet of that H2. Don't flatten everything to H2s or bury defining attributes
  in H3s.
- **Position** encodes prominence: the defining attribute and the snippet answer go
  high. Search engines and readers both weight early content.
- **Format** encodes context priority: a question-form H2 answered immediately reads as
  a direct answer (good for AEO); a noun-phrase H2 reads as a section. Choose per role.

## Query length → vector breadth

The breadth/length of the contextual vector should track the query network's shape. A
node whose query network is a few tight variations wants a focused vector (fewer, deeper
sections). A node spanning many sub-questions wants a broader vector (more H2s). Don't
pad a narrow topic with sections it can't fill — thin sections lower quality and raise
cost of retrieval.

## Worked example — contextual vector for "why is my espresso sour"

- H1: Why is my espresso sour? *(role: macro context + definitional lead)*
- H2 (question, snippet target): What makes espresso taste sour? → ~40-word extractive
  answer: under-extraction. *(role: definition/cause)*
- H2: The main causes of under-extraction *(defining attributes)*
  - H3: Grind too coarse · H3: Water too cool · H3: Dose/ratio off · H3: Shot pulled too fast
- H2: How to fix a sour shot (step by step) *(values/how-to)*
- H2: Sour vs bitter espresso — how to tell them apart *(comparison; macro-micro border)*
  - grouper question bridging to the "bitter espresso" node
- H2: FAQ *(remaining question network: "is sour espresso safe to drink", etc.)*

## Worked example — contextual vector for "AP automation ROI" (commercial intent)

- H1: Accounts payable automation ROI *(macro context)*
- H2 (snippet target): What ROI does AP automation deliver? → extractive answer that
  states the *model*, not an invented figure (see semantic-writing-rules.md).
- H2: The cost drivers AP automation removes *(defining attributes: cost per invoice,
  error rate, cycle time)* — figures only if grounded/locked.
- H2: How to build an AP automation business case *(values/how-to)*
- H2: AP automation ROI vs the cost of manual processing *(comparison)*
- H2: When AP automation does NOT pay off *(edge cases; honest, builds trust)*
- CTA appropriate to commercial intent.
