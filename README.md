# Semantic SEO Suite

**Grounded semantic SEO, GEO & off-page — as Claude Code skills. With a fabrication guard that refuses to invent numbers.**

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](./LICENSE) · Free & open · Runs in [Claude Code](https://claude.com/claude-code)

Most "AI SEO" tools quietly fabricate: made-up search volumes, invented "authority scores," hallucinated product claims. This suite is the opposite. It encodes entity-based, topical-authority SEO (plus AEO/GEO and off-page) as a set of Claude Code skills that **tag the provenance of every number** and **refuse to state a fact that isn't grounded**. It's a methodology you run, not a SaaS you rent.

Clone it, open the folder in Claude Code, and talk to it in plain English — the skills trigger on intent.

---

## Why this exists

- **No fabrication.** Every value is `measured`, `derived`, or `asserted`. A bare number is treated as a bug. A built-in guard (`validate_draft.py`) blocks any brand claim that isn't in a locked fact ledger, and any stat without a citation.
- **Built for AI answers, not just blue links.** A dedicated GEO layer optimizes content to be *cited* by ChatGPT, Perplexity, and Google AI Overviews — where buyers increasingly research.
- **The whole funnel.** Foundation → topical map → briefs → drafts → internal links & schema → audit → performance → GEO → backlinks → distribution.
- **Free, private, yours.** No account, no upload. Runs at zero cost (pure LLM) and gets sharper when you plug in free/paid data sources.

## Quickstart (Claude Code)

```bash
git clone https://github.com/<you>/semantic-seo-suite.git
cd semantic-seo-suite
claude            # or open the folder in the Claude Code desktop app
```

Then just ask:

> "Set up the SEO foundation for `mydomain.com`."
> "Build the topical map." · "Write a brief for X, then draft it." · "How do we get cited by ChatGPT?"

The skills (in `skills/`) are discovered automatically. Each reads your brand workspace, respects the grounding tier, writes back artifacts, and labels provenance.

### Try it now (offline, no keys — uses the bundled demo)

```bash
pip install jsonschema pyyaml --break-system-packages     # T0 minimum

# fabrication guard on the demo draft → CLEAN
python scripts/validate_draft.py \
  --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md \
  --locked examples/driftroast/locked-facts.json --brand-terms "DriftRoast"

# quality + citation-readiness scorers
python scripts/draft_quality.py --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md --floor 700
python scripts/aeo_score.py     --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md

# coverage heatmap (open the HTML)
python scripts/map_heatmap.py --map examples/driftroast/topical-map.json --out /tmp/heatmap.html

# every script's self-test
for s in aeo_score draft_quality link_prospects distribution_plan reprioritize_map serpapi_client provenance; do python scripts/$s.py --selftest; done
```

## What's inside — 10 skills

| Skill | What it does |
|---|---|
| **seo-brand-foundation** | Central entity, audience, competitors, EAV attributes, and the **locked-facts** ledger |
| **topical-map-builder** | Pillar/cluster/supporting map + prioritized content calendar |
| **content-brief-generator** | Entity-aware brief: outline, snippet target, do-not-fabricate list |
| **semantic-draft-writer** | Writes the draft, then runs 3 gates: fabrication → quality → AEO |
| **linking-and-schema** | Internal-link plan + JSON-LD structured data per node |
| **semantic-site-auditor** | Coverage gaps, cannibalization, entity drift, orphans |
| **seo-performance-tracker** | Google Search Console feedback loop (rankings, striking-distance, decay) |
| **answer-engine-optimizer** | GEO — makes content citable by ChatGPT / Perplexity / AI Overviews |
| **link-opportunities** | Off-page: backlink prospects, competitor gap, safe anchor mix |
| **content-distribution** | Per-piece channels, repurposing atoms, cadence |

### The three gates every draft passes
1. **`validate_draft.py`** — fabrication guard (hard gate: no naked stats, no unbacked brand claims).
2. **`draft_quality.py`** — depth, examples, specificity, anti-filler (the quality bar).
3. **`aeo_score.py`** — citation-readiness for AI answer engines (a floor to clear).

## Grounding tiers — pay nothing, or plug in data

| Tier | Needs | Adds |
|---|---|---|
| **T0** | nothing | Full methodology on pure LLM + web search. Provenance `asserted`. |
| **T1** | free installs / GSC OAuth | Embeddings (cannibalization/drift), site crawl, Google Search Console. `measured`. |
| **T2** | a SerpApi key | Live SERP signals → data-driven calendar prioritization. `measured`. |

Keys live only in a git-ignored `.env` (copy `.env.example`) — they never enter the repo.

## Repo layout

```
skills/       10 Claude Code skills (SKILL.md each)
framework/    14 methodology docs the skills read
scripts/      25 deterministic helpers (guards, scorers, clients) — most ship --selftest
templates/    JSON schemas + config template
examples/     driftroast — a complete, fictional worked demo brand
brands/        your workspaces (git-ignored)
RUNBOOK.md    how to run every part, by tier
TESTING.md    how to verify the suite yourself
```

## Verify it
See [TESTING.md](./TESTING.md) — every non-trivial script ships a runnable `--selftest`, because a tool about honesty should prove its own.

## About
Built by **Talha** — I build grounded, no-nonsense AI systems ([atelic.ai](https://atelic.ai)). This suite is free and MIT-licensed; use it for your own brand, client work, or ventures. Issues and PRs welcome.

## License
[MIT](./LICENSE).
