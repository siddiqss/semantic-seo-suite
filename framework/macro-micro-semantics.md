# macro-micro-semantics — page-level and sentence-level rules

Two levels of semantics decide whether a page reads as a definitive answer or as
filler. **Macrosemantics** govern the whole page (one topic, one intent, clear
hierarchy). **Microsemantics** govern sentences (precise definitions, co-occurring
terms, extractive answers). `content-brief-generator` enforces the macro level;
`semantic-draft-writer` enforces the micro level; both are checked by the validator.

## Macrosemantics (page level)

- **One macro context per page.** One topic, one intent, one primary entity. This is
  the master rule; most on-page SEO failures are violations of it.
- **Title / H1 / intent alignment.** The title, H1, and the actual content must agree on
  what the page is. A "how to" title with a "best X" body confuses everyone.
- **Answer above the fold.** The core answer/definition appears early — before history,
  before backstory. Lowers cost of retrieval; wins snippets and AI citations.
- **Return to the central entity.** Even tangents bend back to the page's entity and the
  site's central entity. If a section can't, it belongs elsewhere.
- **Coverage matches the query network.** The page addresses the node's query network
  (query-semantics.md) — no major sub-question left unanswered, no unrelated sections
  bolted on.
- **Hierarchy reflects importance.** Defining attributes get prominence and depth;
  common attributes get brevity (eav-modeling.md).

## Microsemantics (sentence level)

The micro level is where "context-rich" actually happens — the sentence-by-sentence
signals that place your content in exactly the right neighbourhood.

- **Definition-first sentences.** Lead a section with what the thing *is*, in a single
  declarative sentence, before elaborating. ("Under-extraction is when water passes
  through the grounds too fast to dissolve enough flavour.")
- **Question → ~40-word extractive answer.** For question-form headings, answer
  immediately in a concise, self-contained ~40-word block that could be lifted as a
  snippet, then elaborate below it.
- **Declarative modality; minimal hedging.** State things plainly. "Espresso uses ~9 bar
  of pressure," not "espresso might generally tend to use around 9 bar or so." Hedging
  dilutes the signal and reads as low confidence. (Hedge only where genuine uncertainty
  exists — and then be specific about the uncertainty.)
- **Co-occurrence / contextual terms.** Naturally include the terms a real expert would
  use near this concept — the microsemantic signals. For "battery lifespan": charge
  cycles, lithium-ion, thermal management, depth of discharge. These are a *by-product*
  of genuine coverage, never a stuffing exercise. If a term doesn't earn its place in a
  real sentence, leave it out.
- **Information density; no fluff.** Every sentence carries semantic value. Cut
  throat-clearing ("In today's fast-paced world…"), restated headings, and filler
  transitions. Density lowers cost of retrieval and signals expertise.
- **Entity prominence.** Name entities explicitly rather than leaning on pronouns; it
  keeps the entity signal strong and disambiguated.
- **Consistency across the network.** State the same fact the same way across pages.
  Consistent information builds a "contextual connection" between nodes even without a
  hyperlink (a link then strengthens it — see internal-linking-rules.md).

## The anti-fabrication layer (micro level)

Microsemantics tempt fabrication: a "confident, declarative, specific" sentence is
exactly the shape of a made-up statistic. Guard rails:

- A **specific factual value** (number, %, price, spec, date, benchmark) is only
  permitted if grounded — cited external source (`measured`) or in the brand's
  `locked-facts.json`. Otherwise state the *relationship or method* without the number.
- **Declarative ≠ invented.** Write plainly about what you *know*; about what you don't,
  write the honest version: "the exact touchless rate depends on invoice mix" beats a
  fabricated "94% touchless." The validator flags naked numerics and unlocked brand
  claims.
- Prefer **ranges and mechanisms** to invented precision when you lack a source, and
  mark illustrative figures as examples.

## How the two levels interact

Good microsemantics on a page with broken macrosemantics still fails — beautifully
written sentences about three different intents on one URL won't rank. Fix the macro
context first (one topic, one intent, right hierarchy), then make each sentence pull its
weight. The brief locks the macro level so the writer can focus on the micro level.

## Quick checklist (used by the validator's lint)
- [ ] One macro context / one intent — no section pulling toward a different intent.
- [ ] Title ↔ H1 ↔ body agree.
- [ ] Definition/answer appears in the first screen.
- [ ] Each question-heading has an adjacent concise extractive answer.
- [ ] Hedge-word density below threshold; declarative voice dominant.
- [ ] No naked factual numbers; brand claims all trace to locked-facts.json.
- [ ] No fluff sentences (throat-clearing, restated headings, empty transitions).
