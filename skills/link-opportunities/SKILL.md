---
name: link-opportunities
description: >
  Plan off-page authority for a brand — find and prioritize backlink opportunities from
  its topical map and competitor set, with a safe anchor-text mix and a competitor
  backlink-gap worksheet. Use whenever the user mentions backlinks, link building, off-page
  SEO, domain authority, digital PR, guest posts, "who should link to us", getting into
  best-of listicles, or why competitors outrank despite thinner content. Discovers real
  prospects via web_search (T1) or DataForSEO backlinks (T2); never invents authority
  numbers, referring domains, or contact emails. Triggers on off-page / link intent broadly.
---

# link-opportunities

The authority layer the content engine omits. A perfect map on a zero-authority domain
still loses to funded incumbents — this plans the external links (and the citations that
travel with them) that make ranking possible. It reads the same brand workspace, respects
the tier, and tags every prospect's provenance.

Read first: `../../framework/off-page-authority.md` (plays, anchor rules, the honesty
line), then `../../framework/eeat-signals.md` (why off-site entity consistency matters).

## Preconditions
- `entity-profile.json` (competitors drive the backlink gap) + `topical-map.json`.
- Prospect *discovery* needs `web_search: true` (T1) or `dataforseo: true` (T2). At T0 the
  skill produces the plan, plays, and anchor mix but cannot name real prospects — say so;
  do not invent domains.

## Workflow

1. **Build the plan skeleton (T0, offline).**
   ```
   python ../../scripts/link_prospects.py --map brands/<slug>/topical-map.json \
     --entity-profile brands/<slug>/entity-profile.json --brand "<Brand>" \
     --out brands/<slug>/outreach/link-plan.md
   ```
   Emits, per node (priority-ordered core→outer): the fitting plays, an off-page anchor
   mix, and a competitor backlink-gap worksheet. Priorities are `derived`; play notes are
   `asserted`.

2. **Discover real prospects.**
   - **T1 (web_search):** for top-priority commercial nodes, search the target query +
     "best/ alternatives/ vs" and record the listicles/reviews that already rank —
     inclusion targets. For each competitor, search their brand + "review / integration /
     alternative" to surface sites already covering the category.
   - **T2 (DataForSEO backlinks):** pull each competitor's referring domains, filter for
     topical relevance, and rank the gap. Authority numbers here are `measured`.
   - Record every prospect with: URL, why-relevant, authority (`measured` **or** left
     blank — never guessed), the node it supports, and the play. Score with
     `link_prospects.py:score_prospect` (unknown authority scores on relevance + link
     type, flagged unknown).

3. **Write the outreach queue** → append to `brands/<slug>/outreach/link-plan.md`:
   - Ranked prospect table (prospect · node · play · authority[measured|unknown] · angle).
   - Suggested anchor per placement, drawn from the node's anchor examples, honoring the
     mix (keep exact-match ~10%).
   - **No fabricated contacts.** If you can't find a real, published contact, mark it
     "contact: research needed" — do not invent an email.

4. **Feed the loop.**
   - A high-priority node with no realistic prospects → recommend building a *linkable
     asset* for it (free tool / data study), not low-value link spam.
   - Queries where competitors are linked/cited and the brand is absent → shared signal
     with **answer-engine-optimizer**.
   - When a link lands, record the URL on the node; it raises that node in
     **seo-performance-tracker**.

## Definition of done
- `link-plan.md` written: anchor mix, competitor gap worksheet, priority-ordered plays.
- If T1/T2 on: a ranked prospect queue with provenance on every authority value and no
  invented domains or emails. If T0: the plan only, with an explicit note that discovery
  needs web_search/DataForSEO.
- Nothing fabricated — the whole point of doing this inside the suite.

## Grounding ladder
- **T0:** offline plan skeleton, plays, anchor mix, competitor worksheet. Useful alone.
- **T1 (web_search):** + real listicle/review/resource prospects, `measured` + dated.
- **T2 (DataForSEO):** + competitor backlink-gap with `measured` authority numbers.
