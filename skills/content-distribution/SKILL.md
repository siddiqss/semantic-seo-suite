---
name: content-distribution
description: >
  Plan how a brand's published content gets seen — per-piece channel fit, repurposing
  atoms (X thread, LinkedIn post, Reddit answer, short-form video, newsletter), and a
  promotion cadence anchored to the publishing calendar. Use whenever the user asks how to
  promote or distribute content, repurpose a post, where to share an article, build a
  launch or content-promotion plan, drive traffic before SEO kicks in, or "we published
  it, now what". Matches channels to the brand's real personas; invents no reach numbers.
  Triggers on distribution / promotion / repurposing intent broadly.
---

# content-distribution

Publishing isn't distribution. The map decides what to write; this makes sure each piece
is *seen* while organic traffic is still compounding. It reads the same workspace,
respects the tier, and points its plays at the brand's actual personas — not a generic
channel list.

Read first: `../../framework/content-distribution.md` (atoms, channel fit, cadence, the
honesty rule).

## Preconditions
- `entity-profile.json` (audience + personas drive channel fit) + `topical-map.json`
  (statuses tell published from planned).
- Naming the *specific* communities/newsletters needs `web_search: true` (T1). At T0 the
  plan proposes channel types + atoms + cadence but not named venues — say so; don't
  invent subreddits or metrics.

## Workflow

1. **Build the plan (T0, offline).**
   ```
   python ../../scripts/distribution_plan.py --map brands/<slug>/topical-map.json \
     --entity-profile brands/<slug>/entity-profile.json --brand "<Brand>" \
     --out brands/<slug>/outreach/distribution-plan.md
   ```
   Per node (published first, then core→outer): fitting channels, the repurposing atoms,
   and a cadence. Priorities/channel fit are `derived`; the atoms are `asserted` formats.

2. **Find the real venues (T1, web_search).** For the top personas, discover the specific
   subreddits, Slack/Discord communities, newsletters, and creators the ICP actually uses.
   Record each `measured` + dated with why-relevant. Never assert a community exists
   without checking; never attach a reach/engagement estimate.

3. **Write the distribution plan** → `brands/<slug>/outreach/distribution-plan.md`:
   - Priority-ordered pieces with channels, atoms, cadence.
   - The named venues per persona (`measured`), or an explicit note they weren't looked up
     (T0).
   - For a product that can demo itself (e.g. an AI video tool), flag the *dogfood* atom — generate
     the short-form asset with the product; the promo and the demo are one.

4. **Feed the loop.**
   - Community questions worth answering → query-network additions via
     **topical-map-builder**.
   - A link or citation earned while promoting → hand to **link-opportunities** /
     **answer-engine-optimizer**.
   - Once GSC has data, **seo-performance-tracker** shows which distributed pieces
     actually converted attention to rankings.

## Definition of done
- `distribution-plan.md` written: priority-ordered, channels + atoms + cadence per piece.
- Channels tied to the brand's real personas; venues `measured` (T1) or explicitly not
  looked up (T0). No invented reach numbers, no invented communities.

## Grounding ladder
- **T0:** offline channel types, repurposing atoms, cadence. Useful alone.
- **T1 (web_search):** + named communities/newsletters/creators for the ICP, `measured`.
- **T2:** no paid dependency.
