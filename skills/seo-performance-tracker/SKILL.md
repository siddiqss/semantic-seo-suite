---
name: seo-performance-tracker
description: >
  Track topical-map performance from Google Search Console — per-pillar impressions/
  clicks/position rollups, striking-distance opportunities, decaying pages, measured
  cannibalization, and GSC queries the map doesn't yet cover. Use whenever the user asks
  how content is performing, wants a GSC/Search Console report, mentions rankings,
  impressions, clicks, or asks what to update or write next based on real data. Requires
  GSC access; degrades honestly if it's not configured. Triggers on performance/analytics
  intent broadly.
---

# seo-performance-tracker

The measured feedback loop. It replaces guesswork (and the fabricated "Pillar Page Rank"
that wrapper tools invent) with real Search Console data joined to the topical map. Every
figure is `measured` (GSC) or `derived` (rollups) — never estimated.

Read first: `../../framework/topical-map-theory.md` (pillars/priority),
`../../framework/query-semantics.md` (query networks → new nodes).

## Preconditions
- `topical-map.json` with `url`s on published nodes (the auditor sets these).
- GSC configured: `grounding.sources.gsc: true` + `credentials.gsc_credentials_path`.
  If not configured, say so and do NOT invent metrics — spot-checking positions via
  web_search is unreliable; be explicit about that limitation.

## Workflow

1. **Pull GSC data:**
   ```
   python ../../scripts/gsc_client.py --site "<property>" --creds <path> \
     --start <date> --end <date> --dims query,page \
     --out brands/<slug>/data/gsc/pull.json
   # optional prior period for decay:
   python ../../scripts/gsc_client.py ... --start <earlier> --end <earlier> \
     --out brands/<slug>/data/gsc/prev.json
   ```

2. **Analyse against the map:**
   ```
   python ../../scripts/gsc_analyze.py --gsc brands/<slug>/data/gsc/pull.json \
     [--gsc-prev brands/<slug>/data/gsc/prev.json] \
     --map brands/<slug>/topical-map.json --brand "<Brand>" \
     --out brands/<slug>/audits/<date>-performance.md
   ```
   Produces:
   - **Pillar rollups** — impressions/clicks/avg-position per pillar (`derived`). The
     honest Pillar Page Rank.
   - **Striking-distance** — queries at position 5–15 → quick-win update targets.
   - **Measured cannibalization** — one query landing on multiple pages (the strongest
     cannibalization signal; confirms/ː refutes the auditor's embedding guess).
   - **Decaying pages** — >30% click loss vs the prior period.
   - **Uncovered queries** — GSC queries not in any node's query network → candidate new
     map nodes.

3. **Feed the loop:**
   - Add uncovered-query candidates to the map via **topical-map-builder** (as new nodes
     or as query-network additions to existing nodes).
   - Mark striking-distance and decaying nodes `needs-update`; push them up `calendar.md`.
   - Send confirmed measured-cannibalization pairs to **semantic-site-auditor** /
     **linking-and-schema** for consolidation/redirect.

## Definition of done
- Performance report produced with all five sections, every figure provenance-tagged.
- Actionable next steps flowed back into map + calendar.
- If GSC isn't configured: an honest "not available" with the setup pointer, no invented
  numbers.

## Grounding ladder
- **T1 (GSC):** the whole skill — this is a T1 capability (GSC is free).
- **Without GSC:** the skill explains it can't measure performance reliably and points to
  README GSC setup. It does not fabricate a substitute.
