# RUNBOOK — using, running, and testing the Semantic SEO Suite

## 0. What you have
- `semantic-seo-suite/` — Claude Code repo: 10 skills, 14 framework docs, 25 scripts,
  schemas/templates, and a complete worked demo brand (`driftroast`) under `examples/`.
- `dist/packaged/*.skill` — the 10 skills as installable files for claude.ai.

There are two ways to run it: **Claude Code** (skills auto-trigger — recommended) or
**claude.ai** (install the `.skill` files). And a third thing you can always do: run the
**scripts directly** to test the logic.

---

## 1. Install (by tier)

```bash
unzip semantic-seo-suite.zip && cd semantic-seo-suite
# T0 (zero grounding) — required minimum:
pip install jsonschema pyyaml --break-system-packages
# T1 (free grounding): embeddings, crawl, trends, GSC
pip install sentence-transformers trafilatura pytrends beautifulsoup4 \
            google-api-python-client google-auth-oauthlib --break-system-packages
# T2 (paid): SerpApi (current) or DataForSEO — both use only stdlib; set the key in .env (section 5).
```

T0 needs no accounts or keys. T1 needs only pip installs (+ a one-time GSC OAuth if you
want performance tracking). T2 needs a SerpApi key (current provider) or a DataForSEO login.

---

## 2. Test it right now (offline, uses the bundled DriftRoast demo)

These run anywhere and exercise the core logic:

```bash
# fabrication guard — should print CLEAN, exit 0
python scripts/validate_draft.py --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md \
  --locked examples/driftroast/locked-facts.json --brand-terms "DriftRoast"

# and it should CATCH a bad draft (make one with a fake "99.7%" stat) — exit 1

# draft quality (depth/examples/specificity) + AEO citation-readiness — both advisory scorers
python scripts/draft_quality.py --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md --floor 800
python scripts/aeo_score.py --draft examples/driftroast/drafts/how-to-make-pour-over-coffee.md --schema-dir examples/driftroast/data/schema

# embeddings -> cannibalization + drift (offline fallback, no model download)
python scripts/embed_corpus.py --map examples/driftroast/topical-map.json --out /tmp/v.json --fallback
python scripts/semantic_distance.py pairs    --vecs /tmp/v.json --threshold 0.86
python scripts/semantic_distance.py centroid --vecs /tmp/v.json

# coverage heatmap (open the HTML in a browser)
python scripts/map_heatmap.py --map examples/driftroast/topical-map.json --out /tmp/heatmap.html

# linking plan + JSON-LD
python scripts/linking_plan.py --map examples/driftroast/topical-map.json --brand DriftRoast --out /tmp/links.md
python scripts/schema_jsonld.py --map examples/driftroast/topical-map.json \
  --entity-profile examples/driftroast/entity-profile.json --locked examples/driftroast/locked-facts.json \
  --out-dir /tmp/schema

# full smoke check (schemas valid, artifacts provenance-clean)
python scripts/provenance.py
```

The auditor and GSC analyzer can be tested against the fixtures used during the build, or
against your own crawl/GSC data (sections 4–5).

---

## 3. Use it in Claude Code (the real workflow)

1. Open the folder in Claude Code (`claude` in the repo root, or the desktop app pointed
   at it). The 10 SKILL.md files are discovered automatically.
2. Create a brand workspace:
   ```bash
   mkdir -p brands/<slug>/{briefs,drafts,audits,data/{crawl,serp,embeddings,gsc}}
   cp templates/config.yaml.template brands/<slug>/config.yaml   # edit brand/domain/central_entity; tier: t0
   ```
3. Talk to Claude — the skills trigger on intent:
   - "Set up the SEO foundation for `<domain>`" → **seo-brand-foundation** → `entity-profile.json` + `locked-facts.json`
   - "Build the topical map" → **topical-map-builder** → `topical-map.json` + `topical-map.md` + `calendar.md`
   - "Write a brief for `<node/query>`" → **content-brief-generator** → `briefs/<slug>.md`
   - "Draft it" → **semantic-draft-writer** → validated `drafts/<slug>.md`
   - "Audit `<domain>`" → **semantic-site-auditor** → `audits/<date>-full.md`
   - "Give me the internal links and schema" → **linking-and-schema**
   - "How is content performing?" → **seo-performance-tracker** (needs GSC)
   - "Get us cited by ChatGPT/Perplexity" / "AEO / GEO" → **answer-engine-optimizer**
   - "Find backlink opportunities" / "who should link to us" → **link-opportunities**
   - "How do we promote/distribute this" / "repurpose the post" → **content-distribution**

Each skill reads `config.yaml` first, respects the grounding tier, writes back to
`brands/<slug>/`, and labels provenance. The pipeline is stateful — later skills read
earlier outputs.

---

## 4. Use it in claude.ai

Install the skills: Settings → Capabilities/Skills → upload each `dist/packaged/*.skill`
(or click **Save skill** on the file card). Then ask the same questions in chat. Note:
claude.ai runs the skills' reasoning; for the script-heavy steps (crawl, embeddings, GSC)
use Claude Code, which can execute them.

---

## 5. Turn on grounding (T1 / T2)

Edit `brands/<slug>/config.yaml → grounding` (set `tier` and flip individual `sources`).

```bash
# T1: real embeddings for a brand's map
python scripts/embed_corpus.py --map brands/<slug>/topical-map.json \
  --out brands/<slug>/data/embeddings/map.npz
# T1: crawl + audit a real site
python scripts/crawl_sitemap.py --domain <domain> --out /tmp/urls.json
python scripts/extract_page_content.py --urls /tmp/urls.json --out-dir brands/<slug>/data/crawl
python scripts/audit_site.py --map brands/<slug>/topical-map.json \
  --crawl-dir brands/<slug>/data/crawl --entity-profile brands/<slug>/entity-profile.json \
  --brand "<Brand>" --out brands/<slug>/audits/live-audit.md
# T1: query expansion / entity grounding
python scripts/fetch_autocomplete.py --seed "your seed query"
python scripts/wikidata_entity.py --query "your central entity"

# T2 (SerpApi — current provider): put SERPAPI_KEY in .env (gitignored), then
set -a && source .env && set +a
python scripts/serpapi_client.py signals --keywords "kw1,kw2" --cache-dir brands/<slug>/data/serp > signals.json
python scripts/reprioritize_map.py --map brands/<slug>/topical-map.json \
  --signals signals.json --calendar brands/<slug>/calendar.md
# > 100 searches require SERPAPI_CONFIRM=1 (bills per search).
# SerpApi has no keyword volume; prioritization uses measured SERP signals (PAA/related
# breadth = demand, top-10 sitelink authority = difficulty, ad count = commercial pull).
# DataForSEO client (dataforseo_client.py) remains for volume if a working account exists.

# GSC performance (one-time OAuth): put creds json path in config, then
python scripts/gsc_client.py --site "https://<domain>/" --creds <creds.json> \
  --start 2026-04-01 --end 2026-06-30 --out brands/<slug>/data/gsc/pull.json
python scripts/gsc_analyze.py --gsc brands/<slug>/data/gsc/pull.json \
  --map brands/<slug>/topical-map.json --brand "<Brand>" --out brands/<slug>/audits/perf.md
```

---

## 6. Optional: tune skill triggering (needs Claude Code + `claude` CLI)
```bash
python -m scripts.run_loop --eval-set skills/<skill>/evals/evals.json \
  --skill-path skills/<skill> --model <your-model-id> --max-iterations 5 --verbose
```
Apply the returned `best_description` to that skill's SKILL.md frontmatter.

---

## 7. First real payoff
Run **seo-brand-foundation → topical-map-builder** on your own domain (T0, 5 min), then
crawl + **semantic-site-auditor** on a services-business prospect's site — the audit
report (gaps, cannibalization, drift, all provenance-tagged, no fake numbers) is your
pre-sales artifact.

## Troubleshooting
- *Model download fails on embeddings* → add `--fallback` for offline hashing embeddings
  (coarse but works); use a real model backend for decisions.
- *A live script errors on network/creds* → it degrades and tells you which tier is off;
  the pipeline continues at the lower tier.
- *A `.skill` won't upload* → descriptions can't contain `<`/`>`; keep one SKILL.md per
  skill folder (the packager enforces both).
