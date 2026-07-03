# internal-linking-rules — hub-and-spoke, up/down/lateral

Internal links are how the topical map becomes a *graph* a search engine can read.
They distribute relevance and PageRank inside the site and make the pillar→cluster
→supporting hierarchy legible. This doc governs the link skeleton in the map, the link
targets in briefs, and the full plan produced by `linking-and-schema`.

## Hub-and-spoke

Pillars are hubs; clusters and supporting pages are spokes.
- **Down-links:** a pillar links down to each of its clusters; a cluster links down to
  its supporting pages. Hubs distribute authority to spokes.
- **Up-links:** every spoke links up to its parent (cluster→pillar, supporting→cluster).
  Spokes concentrate relevance back on the hub.
- **Lateral links:** between siblings/nodes that share an attribute, *only when
  semantically justified*. Laterals are the most abused link type — see below.

## The three link roles (what goes in a node's internal_links)
- `up` — parent chain. Almost always exactly the parent.
- `down` — children. All of them.
- `lateral` — sibling/related nodes sharing a real attribute or forming a natural
  next-question. Sparse and justified, not "related posts" spray.

## When a lateral link is justified
A lateral link is warranted when the two nodes share an attribute or one is the natural
next question from the other (the grouper-question bridge, contextual-vectors.md).

- **T0:** justify by explicit reasoning — name the shared attribute or the query
  relationship. If you can't name it, don't add the link.
- **T1+:** justify by embedding distance — the two nodes' content/query networks are
  within `lateral_link_threshold` (config). `semantic_distance.py` provides the number;
  record it as the justification (`derived`).

Reject laterals that only share surface words but different intents (linking "how
espresso works" to "best espresso machine" muddies both).

## Anchor text
- **Descriptive, varied, natural.** The anchor should describe the target's topic in
  words a human would use — drawn from the target node's query network for variety.
- **No exact-match spam.** Don't point ten links at one page all reading "best espresso
  machine." Vary anchors across the query network; over-optimised anchors are a risk
  signal and read badly.
- **Contextual placement.** Place the link where the linked concept is actually
  discussed, not in a footer dump. A link inside relevant prose passes more context.

## Contextual connection without a link
Consistent, aligned information across two nodes creates a "contextual connection" even
with no hyperlink (macro-micro-semantics.md rule 11). A hyperlink *strengthens* an
existing contextual connection; it doesn't manufacture one. So: get the content
consistent first, then link.

## Orphans and over-linking (audit signals)
- **Orphan:** a published node with no incoming internal links — it can't receive
  relevance/PageRank. `semantic-site-auditor` flags orphans; fix by adding up/lateral
  links from related nodes.
- **Over-linked hub:** a page with an unnatural number of incoming exact-match links —
  dilutes anchor signal and looks manipulative. Flagged too; fix by pruning/varying.
- **Dead-end:** a page with no outgoing links to the rest of its cluster — leaks the
  reader out of the topic. Add down/lateral links.

## Outer → core flow (critical)
Every outer-section node must have a link path into the core (topical-map-theory.md).
Outer pillars pass authority down to their clusters, which link laterally into the
relevant core node. If an outer node can't justify a link into core, question whether it
belongs on the site at all.

## Worked example — DriftRoast "brewing methods" cluster
(from the shipped demo in `examples/driftroast/`)
- Pillar `n-001` (Coffee brewing methods) → down to `n-002` (pour-over) and `n-003`
  (espresso basics).
- Cluster `n-003` (Espresso basics) → up to `n-001`; lateral to `n-004` (sour espresso
  fixes — shared attribute: espresso troubleshooting, a natural next question).
- Supporting `n-004` (sour espresso) → up to `n-003`; it earns its place by resolving a
  problem the pillar raises, which is the support→cluster bridge.

Anchors vary: from `n-001`, link to `n-002` as "brewing a pour-over" in one place and
"the pour-over method" in another — same target, different query-network phrasings.
