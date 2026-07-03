#!/usr/bin/env python3
"""
serpapi_client.py — thin SerpApi (serpapi.com) client. Replaces DataForSEO for T2.

SerpApi returns live Google SERP JSON but NOT keyword search volume. So instead of a
fabricated volume, we extract honest, directly-observable SERP signals per query and let
reprioritize_map.py score on them:

  ads_count         paid advertisers on the SERP        -> commercial competition/value
  paa_count         People-Also-Ask questions           -> informational demand breadth
  related_count     related searches                    -> topic interest breadth
  organic_authority top-10 organic results w/ sitelinks -> incumbent strength (difficulty)

Every value is `measured` (source: serpapi) — counted from the response, never estimated.

Credentials from env only (SERPAPI_KEY). Caches per query (SerpApi bills per search).

Usage:
  export SERPAPI_KEY=...
  python serpapi_client.py signals --keywords "ai ugc ads,best ai ugc ad tools" \
      --location "United States" --cache-dir brands/<slug>/data/serp > signals.json
  python serpapi_client.py serp --keyword "best ai ugc ad tools" --cache-dir data/serp
  python serpapi_client.py --selftest
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, urllib.parse, urllib.request

BASE = "https://serpapi.com/search.json"
COST_WARN_THRESHOLD = int(os.environ.get("SERPAPI_WARN_THRESHOLD", "100"))

def _cost_guard(n):
    if n > COST_WARN_THRESHOLD and os.environ.get("SERPAPI_CONFIRM") != "1":
        sys.stderr.write(f"[serpapi] COST GUARD: about to run {n} searches (> "
                         f"{COST_WARN_THRESHOLD}); SerpApi bills per search. Re-run with "
                         f"SERPAPI_CONFIRM=1 to proceed, or lower the batch.\n")
        raise SystemExit(3)

def _key():
    k = os.environ.get("SERPAPI_KEY")
    if not k:
        sys.stderr.write("[serpapi] SERPAPI_KEY not set — T2 disabled. Degrade to T0/T1.\n")
        return None
    return k

def _get(params, cache_dir=None, retries=2, timeout=60):
    ck = hashlib.md5(json.dumps({k: v for k, v in params.items() if k != "api_key"},
                                sort_keys=True).encode()).hexdigest()[:20]
    cache = os.path.join(cache_dir, f"serpapi_{ck}.json") if cache_dir else None
    if cache and os.path.exists(cache):
        return json.load(open(cache))
    url = BASE + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8", "ignore"))
            if cache:
                os.makedirs(cache_dir, exist_ok=True); json.dump(data, open(cache, "w"))
            return data
        except Exception as e:            # timeout / transient network — retry, then give up on THIS keyword
            last = e
    raise last

def extract_signals(keyword, data):
    """Count observable SERP features — no estimation."""
    organic = data.get("organic_results") or []
    ads = data.get("ads") or []
    paa = data.get("related_questions") or []
    related = data.get("related_searches") or []
    org_auth = sum(1 for o in organic[:10] if o.get("sitelinks"))
    return {
        "keyword": keyword,
        "ads_count": len(ads),
        "paa_count": len(paa),
        "related_count": len(related),
        "organic_authority": org_auth,
        "provenance": "measured", "source": "serpapi:google_serp",
    }

def one(keyword, location, key, cache_dir):
    params = {"engine": "google", "q": keyword, "location": location,
              "num": 20, "hl": "en", "gl": "us", "api_key": key}
    return extract_signals(keyword, _get(params, cache_dir))

def signals(keywords, location, key, cache_dir):
    _cost_guard(len(keywords))
    out, failed = [], []
    for k in keywords:
        k = k.strip()
        if not k:
            continue
        try:
            out.append(one(k, location, key, cache_dir))
        except Exception as e:            # one bad keyword must not sink the whole batch
            failed.append(k)
            sys.stderr.write(f"[serpapi] skipped '{k}': {e}\n")
    if failed:
        sys.stderr.write(f"[serpapi] {len(failed)} keyword(s) failed after retries; "
                         f"re-run to pick them up from cache: {failed}\n")
    return out

def selftest():
    # a representative SerpApi payload -> exact counts
    payload = {
        "organic_results": [{"sitelinks": {"expanded": [1]}}, {}, {"sitelinks": {"inline": [1]}}] + [{}] * 7,
        "ads": [{}, {}, {}],
        "related_questions": [{}, {}, {}, {}],
        "related_searches": [{}, {}],
    }
    s = extract_signals("kw", payload)
    assert s["ads_count"] == 3 and s["paa_count"] == 4 and s["related_count"] == 2, s
    assert s["organic_authority"] == 2, s          # only 2 organic have sitelinks
    assert s["provenance"] == "measured"
    # empty SERP -> all zero, still measured (not fabricated)
    z = extract_signals("kw", {})
    assert z["ads_count"] == 0 and z["organic_authority"] == 0
    print("selftest ok — SERP signal extraction counts match, empty SERP stays zero/measured")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["signals", "serp"])
    ap.add_argument("--keywords"); ap.add_argument("--keyword")
    ap.add_argument("--location", default="United States")
    ap.add_argument("--cache-dir")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    key = _key()
    if not key:
        sys.exit(0)  # graceful degrade, per suite convention
    if a.cmd == "signals":
        kws = [k for k in (a.keywords or "").split(",") if k.strip()]
        print(json.dumps(signals(kws, a.location, key, a.cache_dir), indent=2))
    elif a.cmd == "serp":
        print(json.dumps(one(a.keyword, a.location, key, a.cache_dir), indent=2))
    else:
        print("error: give a command (signals|serp) or --selftest", file=sys.stderr); sys.exit(2)

if __name__ == "__main__":
    main()
