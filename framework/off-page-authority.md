# Off-Page Authority (Link Opportunities)

The on-page suite makes a site *deserve* to rank. Off-page authority is what lets it
*actually* rank against funded incumbents: external sites vouching for yours. This is the
layer the content engine deliberately omitted — a great map on a zero-authority domain
still sits on page three.

The same non-negotiable overlay applies, and it matters more here than anywhere else:
**backlink land is full of fabricated metrics.** Wrapper tools quote made-up domain
authority, guess contact emails, and invent "link scores." The suite's rule holds the
line: a referring domain, an authority number, a contact — each is `measured` (pulled
from a real source, dated) or it does not appear. Unknown authority stays *unknown*, never
a guess (`scripts/link_prospects.py:score_prospect` enforces this).

## What earns links (and citations)

Links follow value, not requests. The plays that work, roughly in order of ROI for a
tool-category brand:

1. **Listicle inclusion** — get added to the "best/top AI UGC tools" roundups that
   *already rank* for your commercial queries. One inclusion on a ranking listicle beats
   ten low-value links, and it's where buyers (and LLMs) look.
2. **Competitor backlink gap** — pull the referring domains linking to each competitor
   (they're in `entity-profile.json`), filter for topical relevance, pitch the same
   sites. Someone who links to Arcads or Creatify will consider you.
3. **Comparison / review sites** — reviewers and comparison directories covering the
   category; often the same sources LLMs synthesize "X vs Y" answers from.
4. **Resource pages** — curated guide/resource lists in DTC and paid-social niches.
5. **Digital PR / data** — pitch a *grounded* stat or original data (from
   `locked-facts.json`) to journalists and newsletters. Never pitch an invented number.
6. **Guest posts** — contributed articles on ecommerce/marketing blogs, linking a pillar.
7. **Community** — Reddit/Quora/Slack answers: usually nofollow, but they drive referral
   traffic and, increasingly, AI citations — so they feed `answer-engine-optimizer` too.

## Anchor text off-page ≠ on-page

Internal anchors (see `internal-linking-rules.md`) can be descriptive and exact-match.
External anchors must *not* be — a backlink profile heavy on exact-match commercial
anchors is a classic penalty signal, because natural links rarely use your target
keyword. Target mix (enforced in `link_prospects.py`):

| Style | Share | Example |
|---|---|---|
| Branded | 40% | "YourBrand", "YourBrand's guide" |
| Natural / generic | 25% | "this guide", "here" |
| Topic / partial | 25% | "AI UGC ads", "how UGC ads work" |
| Exact-match | 10% | "best AI UGC ad tools" — use sparingly |

You control anchors only where you place the link (guest posts, profiles). For earned
links you take what you get — this mix is the *target across the profile*, not a demand.

## Priority

Point authority where it converts and where it's winnable: **core-section pillars first**
(they monetize and they're the hardest to rank), then core clusters, then outer feeders.
`link_prospects.py:priority()` scores this from the map so the plan is ordered, not a
flat wishlist.

## The honest limit

This layer *plans and targets*. It builds a prioritized prospect list, the anchor mix,
and the competitor gap worksheet. It does **not** send outreach or build relationships —
a script can't email a blogger or earn trust. Expect an ordered queue and pitch angles;
a human (or an outreach agent) does the sending. Anyone selling automated backlinks is
selling the kind of links that get sites penalized.

## Feed the loop
- A high-priority node with no realistic prospects yet → a signal to build a *linkable
  asset* (free tool, data study) for it, not to spam low-value links.
- A query where competitors are cited/linked and you're absent → shared signal with
  `answer-engine-optimizer` (citation and links correlate).
- Landed links on a node → record the URL; it raises that node's odds in
  `seo-performance-tracker`, closing the loop back to measured ranking.
