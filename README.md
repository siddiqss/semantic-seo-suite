# Semantic SEO Suite

**A free, open-source alternative to Surfer, MarketMuse, Clearscope & Frase — built as Claude Code skills. Topical authority, content briefs, AI writing, schema, GEO, and backlinks. With a fabrication guard that refuses to invent numbers.**

<p align="center">
  <img src="assets/overview.svg" alt="Semantic SEO Suite — entity-based topical map, entity-aware briefs, fabrication-guarded AI drafts, schema, GEO, and backlinks; every number tagged measured / derived / asserted" width="900">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](./LICENSE) · Free forever · [![Runs in Claude Code](https://img.shields.io/badge/Runs%20in-Claude%20Code-D97757?logo=claude&logoColor=white)](https://claude.com/claude-code) · No SaaS, no seat fees

Paid "AI SEO platforms" cost $50–$1,000+/month and quietly fabricate: made-up search volumes, invented "content scores," hallucinated product claims. This suite does the same jobs — **entity-based topical mapping, content-gap analysis, keyword clustering, content briefs, on-page optimization, internal linking, schema markup, rank tracking, and answer-engine optimization** — as skills you run inside Claude Code, for free, with the provenance of every number tagged and a guard that blocks any claim that isn't grounded.

Clone it, open the folder in Claude Code, talk to it in plain English.

---

## Why this instead of a paid SEO tool?

| | **Semantic SEO Suite** | Surfer / MarketMuse / Clearscope / Frase / SemanticOS |
|---|---|---|
| **Price** | Free, MIT, unlimited projects | $50–$1,000+/mo, per-seat, project caps |
| **Where it runs** | Your Claude Code — artifacts are files you own | Their cloud; you rent access |
| **Topical map & authority** | ✅ pillar/cluster/supporting + prioritized calendar | ✅ (their core feature) |
| **Content briefs** | ✅ entity-aware, with a do-not-fabricate list | ✅ |
| **Content optimization score** | ✅ **three** scores: fabrication, quality/depth, AEO | ✅ one proprietary "content score" |
| **Fabrication guard** | ✅ refuses invented stats & unverified brand claims | ❌ no fact guard — AI output can hallucinate |
| **AEO / GEO (get cited by ChatGPT, AI Overviews)** | ✅ dedicated skill + scorer | ⚠️ partial / emerging |
| **Off-page + distribution** | ✅ backlink prospecting + repurposing plans | ❌ usually separate products |
| **Keyword volume / SERP data** | Bring-your-own (SerpApi/GSC) or run free at T0 | Bundled proprietary database |
| **Customizable** | ✅ edit the skills & rulebook yourself | ❌ fixed black box |

**Where paid tools still win (honestly):** they own huge proprietary keyword/SERP databases, polished dashboards, and one-click integrations. This suite trades the UI for transparency, ownership, and zero cost — and lets you plug in the same data via your own SerpApi/GSC keys.

## What you can do

- **Build topical authority** — generate a full pillar → cluster → supporting **topical map** with a prioritized **content calendar** from one central entity.
- **Find content gaps & cannibalization** — audit any site against its map (coverage gaps, keyword cannibalization, entity drift, orphan pages).
- **Cluster keywords into topics** and model your niche as **entities and attributes** (EAV), not a keyword list.
- **Generate content briefs** — entity-aware outlines with snippet targets and internal-link targets.
- **Write on-page-optimized drafts** that pass a **fabrication guard**, a **depth/quality score**, and an **AEO citation score** before they ship.
- **Optimize internal linking & schema** — hub-and-spoke link plans with varied anchors + valid **JSON-LD** per page.
- **Track rankings** from Google Search Console (striking-distance, decay, uncovered queries).
- **Win AI answers (GEO)** — harden content to be cited by **ChatGPT, Perplexity, and Google AI Overviews**.
- **Build backlinks** — prospect lists, competitor backlink-gap, and a penalty-safe anchor mix.
- **Distribute & repurpose** — per-piece channel plans and repurposing atoms.

## What you get (the actual deliverables)

Everything is a file you own, not a dashboard you rent:

- 🗺️ **Topical map** — `topical-map.json` + a readable tree (`topical-map.md`)
- 🔥 **Visual coverage heatmap** — a self-contained `heatmap.html` you open in any browser; color-codes every node by status (`planned → briefed → drafted → published → needs-update`)
- 📅 **Prioritized content calendar** — re-sorted on real SERP signals when you add a key
- 📝 **Content briefs** — per node, with entities, snippet target, and do-not-fabricate list
- ✍️ **Guarded drafts** — Markdown with front-matter, scored on fabrication / quality / AEO
- 🔗 **Internal-linking plan** — up/down/lateral links with varied, safe anchors
- 🏷️ **JSON-LD schema** — one validated file per page (Article/FAQ/HowTo/Product) + org graph
- 🔍 **Audit report** — gaps, cannibalization, drift, orphans, provenance-tagged
- 📈 **Performance report** — GSC rollups, striking-distance, decay
- 🤖 **AEO report** — per-page citation-readiness + a hardening queue
- 🎯 **Link + distribution plans** — prospects, anchors, channels, cadence

> See a complete worked example in [`examples/driftroast/`](./examples/driftroast/) — a fictional coffee brand with a real map, brief, guarded draft (scores: fabrication CLEAN · quality 100 · AEO 92), heatmap, schema, and link plan.

## The 10 skills

| Skill | What it does |
|---|---|
| **seo-brand-foundation** | Central entity, audience, competitors, EAV attributes, locked-facts ledger |
| **topical-map-builder** | Topical map + prioritized content calendar |
| **content-brief-generator** | Entity-aware brief: outline, snippet target, do-not-fabricate list |
| **semantic-draft-writer** | Writes the draft, runs 3 gates (fabrication → quality → AEO) |
| **linking-and-schema** | Internal-link plan + JSON-LD structured data |
| **semantic-site-auditor** | Content-gap, cannibalization, entity-drift, orphan audit |
| **seo-performance-tracker** | Google Search Console feedback loop |
| **answer-engine-optimizer** | GEO — get cited by ChatGPT / Perplexity / AI Overviews |
| **link-opportunities** | Backlink prospecting, competitor gap, safe anchor mix |
| **content-distribution** | Channels, repurposing atoms, cadence |

### The three quality gates (what replaces a fake "content score")
1. **`validate_draft.py`** — fabrication guard: no naked stats, no unbacked brand claims (hard gate).
2. **`draft_quality.py`** — depth, examples, specificity, anti-filler (the bar to beat).
3. **`aeo_score.py`** — citation-readiness for AI answer engines (a floor to clear).

Every number the suite emits is tagged `measured`, `derived`, or `asserted`. A bare number is treated as a bug.

## Grounding tiers — free, or plug in data

| Tier | Needs | Adds |
|---|---|---|
| **T0** | nothing | Full methodology on pure LLM + web search. |
| **T1** | free installs / GSC OAuth | Embeddings (cannibalization/drift), site crawl, Search Console. |
| **T2** | a SerpApi key | Live SERP signals → data-driven calendar prioritization. |

Keys live only in a git-ignored `.env` (copy `.env.example`) — they never enter the repo.

## Quickstart (Claude Code)

```bash
git clone https://github.com/siddiqss/semantic-seo-suite.git
cd semantic-seo-suite
claude            # or open the folder in the Claude Code desktop app
```

Then just ask:

> "Set up the SEO foundation for `mydomain.com`." · "Build the topical map." ·
> "Write a brief for X, then draft it." · "Audit my site." · "How do we get cited by ChatGPT?"

### Try it now (offline, no keys — bundled demo)

```bash
pip install jsonschema pyyaml --break-system-packages

# fabrication guard on the demo draft → CLEAN
python scripts/validate_draft.py \
  --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md \
  --locked examples/driftroast/locked-facts.json --brand-terms "DriftRoast"

# quality + AEO scorers
python scripts/draft_quality.py --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md --floor 700
python scripts/aeo_score.py     --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md

# open the visual coverage heatmap
python scripts/map_heatmap.py --map examples/driftroast/topical-map.json --out /tmp/heatmap.html && open /tmp/heatmap.html

# every script's self-test
for s in aeo_score draft_quality link_prospects distribution_plan reprioritize_map serpapi_client provenance; do python scripts/$s.py --selftest; done
```

Full instructions per tier: [RUNBOOK.md](./RUNBOOK.md). Verify the suite yourself: [TESTING.md](./TESTING.md).

## Repo layout

```
skills/       10 Claude Code skills (SKILL.md each)
framework/    14 methodology docs the skills read
scripts/      25 deterministic helpers (guards, scorers, SERP/GSC clients) — most ship --selftest
templates/    JSON schemas + config template
examples/     driftroast — a complete, fictional worked demo brand
brands/        your workspaces (git-ignored — client data never committed)
```

## About
Built by [Talha Siddique](https://linkedin.com/in/talha-siddique) — Senior Full Stack Engineer and I build grounded, no-nonsense production AI systems ([atelic.ai](https://atelic.ai)). This suite is free and MIT-licensed; use it for your own brand, client work, or ventures. Issues and PRs welcome; star it if it saved you a subscription.

## License
[MIT](./LICENSE).
