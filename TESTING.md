# Testing & verification

The suite's promise is *no fabrication*. So its own checks are runnable — clone the repo
and verify them yourself, no accounts or keys needed.

## Self-tests (offline, deterministic)

Every non-trivial script ships a `--selftest`. All pass on a clean checkout:

```bash
for s in aeo_score draft_quality link_prospects distribution_plan \
         reprioritize_map serpapi_client provenance; do
  python scripts/$s.py --selftest
done
```

| Script | What its self-test proves |
|---|---|
| `validate_draft.py` | Catches naked stats + unbacked brand claims; passes a clean draft (see RUNBOOK §2) |
| `draft_quality.py` | A deep, specific draft (95) scores far above thin filler (32) |
| `aeo_score.py` | Citation-ready structure scores above unstructured prose |
| `reprioritize_map.py` | Business × demand × winnability ordering holds; parses SerpApi **and** DataForSEO |
| `serpapi_client.py` | SERP-signal extraction counts are exact; empty SERP stays zero, never invented |
| `link_prospects.py` | Priority + safe anchor-mix + honest scoring (unknown authority ≠ guessed) |
| `distribution_plan.py` | Published-first priority, channel-fit, cadence invariants |
| `provenance.py` | Flags any bare number with no `measured`/`derived`/`asserted` tag |

## End-to-end on the demo brand

`examples/driftroast/` is a complete, fictional worked brand (specialty coffee). The
offline pipeline runs against it with no keys — see RUNBOOK §2.

## Skill trigger evals

Each skill carries an eval set in `skills/<skill>/evals/evals.json` (prompt + assertions).
The formal trigger-rate optimizer (`run_loop`) needs Claude Code + the `claude` CLI; run
it per skill to tune each `description` (RUNBOOK §6).

## The honest limit
These verify the *mechanics* (no fabrication, correct scoring, honest degradation). They do
not grade taste or truth of the underlying facts — that is what the grounding tiers,
`locked-facts.json`, and human review are for.
