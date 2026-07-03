# brands/ — your workspaces

Each brand you work on lives here as `brands/<slug>/`. This directory is **git-ignored**
so your own (and clients') data never gets committed. A complete worked example ships in
[`../examples/driftroast/`](../examples/driftroast/).

Create one:
```bash
mkdir -p brands/<slug>/{briefs,drafts,audits,data/{crawl,serp,embeddings,gsc}}
cp templates/config.yaml.template brands/<slug>/config.yaml
```
Then talk to Claude Code — the skills trigger on intent (see the root README).
