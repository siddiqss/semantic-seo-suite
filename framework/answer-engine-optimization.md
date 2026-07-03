# Answer-Engine Optimization (AEO / GEO)

Traditional SEO earns a ranked link. Answer engines — Google AI Overviews, ChatGPT,
Perplexity, Gemini, Copilot — earn a *citation inside a synthesized answer*. The reader
often never clicks. For a tool category where buyers research tools directly
inside an LLM, being the *source the model quotes* can matter more than the blue link.

This doc is the GEO half of the suite. It sits beside `macro-micro-semantics.md` (which
already bakes in the writing tactics) and extends `seo-performance-tracker.md` (which
measures Google only). The suite's non-negotiable overlay still holds: **every visibility
claim is `measured`, `derived`, or `asserted` — never invented.** AI-visibility is
especially prone to vibes; the discipline is what keeps it honest.

## What answer engines actually lift

They retrieve and quote *passages*, not pages. A liftable passage is:

1. **Extractive** — answers a question in the first 1–3 sentences, before backstory.
2. **Self-contained** — makes sense pasted alone; no dangling "This/It/That" opener, no
   dependency on the paragraph above.
3. **Definition-first** — leads with what the thing *is* in one tight declarative line.
4. **Structured** — lists and comparison tables are quoted verbatim far more than prose.
5. **Grounded** — a specific, attributable fact (with a source) beats a hedge.
6. **Machine-legible** — backed by JSON-LD so the entity and claims are unambiguous.

`scripts/aeo_score.py` scores a draft on exactly these signals (DEF, QA, TLDR, LIFT,
BREV, SELF, SCHEMA → 0–100). It is advisory, not a fabrication gate — run it *after*
`validate_draft.py` passes.

## The two jobs

### 1. Harden content to be citable (T0, offline, deterministic)
Score every core-section draft with `aeo_score.py`; fix what it flags. The highest-value
moves, in order:
- Put a **standalone ≤50-word definition** as the first paragraph — not buried mid-lead.
- Convert key H2s to **questions** and answer each in ≤50 words *immediately*, then
  elaborate below.
- Add at least one **list or comparison table** per commercial page.
- Kill **dangling-pronoun openers** so each paragraph stands alone.
- Attach **JSON-LD** (`linking-and-schema`) — Article/FAQ/Product as fits the node.

Priority: harden **core-section** nodes first (they convert), and comparison/alternative
nodes hardest (LLMs synthesize "best X" answers from exactly these).

### 2. Measure AI visibility (T1, web_search) — honestly
There is no free API that reports "did ChatGPT cite you." Two grounded methods only:
- **`measured` (web_search):** query the target question in an answer-style search and
  record what the engine returns — is the brand named? cited with a link? which
  competitor sources are quoted? Record the query, the engine, the date, and the raw
  observation. This is a spot check, not a rank tracker — label it `measured` but note
  the sample size (n=1 per probe).
- **`asserted`:** qualitative judgement about citation-worthiness from reading the SERP /
  answer. Never emit a "visibility %" or "citation share" number — there is no
  measurement behind it. If you feel the urge to put a number there, that urge is the
  signal to write a provenance tag instead (see `00-overview.md`).

Do **not** build a fake "AI Visibility Score" the way wrapper tools do. Report observed
citations (measured, dated, per-query) and a prioritized hardening list. That is the
honest artifact.

## Where AEO differs from on-page SEO

| Google (ranked link) | Answer engine (citation) |
|---|---|
| Title/meta win the click | First sentence wins the quote |
| Page-level relevance | Passage-level extractability |
| Backlinks drive authority | Being *quotable + grounded* drives inclusion |
| Rank tracked by position | "Visibility" is per-answer, per-engine, spot-checked |
| Keyword in H1 | Question-shaped H2 with a tight answer |

Both matter. AEO is additive to the on-page map, not a replacement — the same nodes,
hardened.

## Feed the loop
- Nodes scoring `<70` on `aeo_score.py` → mark `needs-update`, push up `calendar.md`.
- A target query where competitors are cited and the brand is not → a hardening task on
  the owning node (and a signal for `link-opportunities`, since citation often follows
  authority).
- New questions surfaced while probing answer engines → candidate query-network
  additions via `topical-map-builder`.
