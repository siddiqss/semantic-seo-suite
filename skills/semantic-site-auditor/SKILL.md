---
name: semantic-site-auditor
description: >
  Audit an existing site against its topical map — coverage gaps, keyword
  cannibalization, entity drift, orphan pages, and per-page micro-semantic issues. Use
  whenever the user asks to audit a site, find content gaps, check for cannibalization,
  asks "why aren't we ranking", wants to know what's missing from their niche coverage,
  or wants a pre-sales content audit of any domain. Produces a prioritised audit report
  with provenance on every finding. Triggers on audit/gap/cannibalization intent broadly.
---

# semantic-site-auditor

Turn a live site + its topical map into a prioritised, evidence-backed fix list. Every
finding carries provenance (`measured` from crawl, `derived` from embeddings) — no
invented scores. This is also the strongest pre-sales artifact for services work: run it
on a prospect's domain before a call.

Read first: `../../framework/topical-map-theory.md` (gap/section logic),
`../../framework/internal-linking-rules.md` (orphans), `../../framework/eav-modeling.md`
(drift = claimed vs perceived identity).

## Preconditions
- `brands/<slug>/config.yaml` (tier).
- A `topical-map.json` to audit against. If none exists, run **topical-map-builder**
  first (you can't measure coverage without a target map).
- `entity-profile.json` (for the claimed-identity centroid used by drift).

## Workflow

1. **Crawl + extract** the site into `brands/<slug>/data/crawl/`:
   ```
   python ../../scripts/crawl_sitemap.py --domain <domain> --max-pages 500 --out /tmp/urls.json
   python ../../scripts/extract_page_content.py --urls /tmp/urls.json --out-dir brands/<slug>/data/crawl
   ```
   Robustness: `crawl_sitemap.py` falls back to a same-domain BFS when there's no
   sitemap, respects robots.txt, and caps pages/depth. For JS-rendered sites, extraction
   may be thin — note that in the report rather than treating missing content as a gap.

2. **Run the analysis engine:**
   ```
   python ../../scripts/audit_site.py \
     --map brands/<slug>/topical-map.json --crawl-dir brands/<slug>/data/crawl \
     --entity-profile brands/<slug>/entity-profile.json \
     --locked brands/<slug>/locked-facts.json --brand "<Brand>" \
     --out brands/<slug>/audits/<date>-full.md
   ```
   It matches each page to its nearest map node (embedding cosine) and reports:
   - **Coverage gaps** — nodes with no matching page (`derived`).
   - **Cannibalization** — page pairs with high similarity + same intent, and any node
     hit by multiple pages (`derived`).
   - **Entity drift** — pages farthest from the core-section centroid, i.e. content
     pulling the site away from its claimed identity (`derived`). At T0 (no embeddings),
     do this qualitatively and label it `asserted` — never emit a fake distance.
   - **Orphans** — pages with no incoming internal links (`measured` from the crawl link
     graph).
   - **Micro-audit** — per-page lint (naked stats, fluff, unanswered question headings)
     reusing the draft rules.

3. **Review + prioritise.** The report ends with a prioritised action list:
   **create** (gap), **consolidate/redirect** (cannibalization), **rewrite/relink or
   prune** (drift), **relink** (orphan). Sanity-check each finding — with the offline
   hash-fallback embeddings, similarities are coarse; re-run with a model backend before
   making irreversible calls (redirects/prunes).

4. **Feed back into the map.** Apply `status_updates` from the audit JSON (matched nodes
   → `published` with their URL); mark thin/drifting matched nodes `needs-update`; add
   the confirmed gaps to `calendar.md` as new priorities.

5. **Render the heatmap** (`../../scripts/map_heatmap.py`) after status updates so
   coverage is visible at a glance.

## Definition of done
- Report produced with all five finding types, each provenance-tagged.
- At least one finding is verifiable by hand (a true gap or a true cannibalization pair).
- Map statuses updated; gaps flowed into the calendar.
- No fabricated scores anywhere (drift/cannibalization are `derived` or clearly `asserted`).

## Grounding ladder
- **T0:** crawl + extract still work (they're just HTTP); matching/cannibalization/drift
  are LLM-qualitative and labeled `asserted`. Orphans + micro-audit are `measured`.
- **T1:** embedding-based matching/cannibalization/drift (`derived`) — the real version.
- **T1+GSC:** confirm cannibalization with pages sharing top queries in Search Console
  (the strongest, `measured` signal) — see seo-performance-tracker.
