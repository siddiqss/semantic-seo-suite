#!/usr/bin/env python3
"""
dataforseo_client.py — thin DataForSEO client for keyword volume/difficulty, live SERP,
and People-Also-Ask. Credentials from env only (DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD),
never from config files. Caches responses to a directory (DataForSEO bills per request).

Live network + paid account required. Gated: if creds are absent it exits cleanly with a
message, so callers degrade to T0/T1 instead of failing.

Usage:
  export DATAFORSEO_LOGIN=... DATAFORSEO_PASSWORD=...
  python dataforseo_client.py volume --keywords "ugc ads,ai ugc ads" --location US --cache-dir data/serp
  python dataforseo_client.py serp --keyword "best ai ugc ad tools" --location US --cache-dir data/serp
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, sys, urllib.request

BASE = "https://api.dataforseo.com/v3"

# DataForSEO bills per request/keyword. Warn (and require opt-in) before large batches.
COST_WARN_THRESHOLD = int(os.environ.get("DATAFORSEO_WARN_THRESHOLD", "100"))

def _cost_guard(n_items, kind):
    if n_items > COST_WARN_THRESHOLD and os.environ.get("DATAFORSEO_CONFIRM") != "1":
        sys.stderr.write(
            f"[dataforseo] COST GUARD: about to request {kind} for {n_items} items "
            f"(> {COST_WARN_THRESHOLD}). DataForSEO bills per request. Re-run with "
            f"DATAFORSEO_CONFIRM=1 to proceed, or lower the batch size.\n")
        raise SystemExit(3)

def _creds():
    lo, pw = os.environ.get("DATAFORSEO_LOGIN"), os.environ.get("DATAFORSEO_PASSWORD")
    if not lo or not pw:
        sys.stderr.write("[dataforseo] DATAFORSEO_LOGIN/PASSWORD not set — T2 disabled. "
                         "Caller should degrade to T0/T1.\n")
        return None
    return base64.b64encode(f"{lo}:{pw}".encode()).decode()

def _post(path, payload, auth, cache_dir=None):
    key = hashlib.md5((path + json.dumps(payload, sort_keys=True)).encode()).hexdigest()[:20]
    cache = os.path.join(cache_dir, f"{key}.json") if cache_dir else None
    if cache and os.path.exists(cache):
        return json.load(open(cache))
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8", "ignore"))
    if cache:
        os.makedirs(cache_dir, exist_ok=True); json.dump(data, open(cache, "w"))
    return data

def volume(keywords, location, auth, cache_dir):
    _cost_guard(len(keywords), "search_volume")
    payload = [{"keywords": keywords, "location_name": location, "language_code": "en"}]
    data = _post("/keywords_data/google_ads/search_volume/live", payload, auth, cache_dir)
    out = []
    for task in data.get("tasks", []):
        for res in (task.get("result") or []):
            out.append({"keyword": res.get("keyword"),
                        "search_volume": {"value": res.get("search_volume"),
                                          "provenance": "measured", "source": "dataforseo:search_volume"},
                        "competition": res.get("competition")})
    return out

def serp(keyword, location, auth, cache_dir):
    payload = [{"keyword": keyword, "location_name": location, "language_code": "en", "depth": 20}]
    data = _post("/serp/google/organic/live/advanced", payload, auth, cache_dir)
    results, features, paa = [], set(), []
    for task in data.get("tasks", []):
        for res in (task.get("result") or []):
            for item in res.get("items", []):
                t = item.get("type")
                if t == "organic":
                    results.append({"type": "organic", "title": item.get("title"), "url": item.get("url")})
                elif t == "people_also_ask":
                    features.add("people_also_ask")
                    for e in item.get("items", []):
                        if e.get("title"): paa.append(e["title"])
                elif t == "featured_snippet":
                    features.add("featured_snippet")
                elif t in ("shopping", "product"):
                    features.add("shopping"); results.append({"type": "shopping", "title": item.get("title"), "url": item.get("url")})
    return {"query": keyword, "results": results, "features": sorted(features),
            "people_also_ask": paa, "provenance": "measured", "source": "dataforseo:serp"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["volume", "serp"])
    ap.add_argument("--keywords"); ap.add_argument("--keyword")
    ap.add_argument("--location", default="United States")
    ap.add_argument("--cache-dir")
    a = ap.parse_args()
    auth = _creds()
    if not auth:
        print(json.dumps({"disabled": True, "reason": "no credentials"})); return
    if a.cmd == "volume":
        kws = [k.strip() for k in (a.keywords or "").split(",") if k.strip()]
        print(json.dumps(volume(kws, a.location, auth, a.cache_dir), indent=2))
    else:
        print(json.dumps(serp(a.keyword, a.location, auth, a.cache_dir), indent=2))

if __name__ == "__main__":
    main()
