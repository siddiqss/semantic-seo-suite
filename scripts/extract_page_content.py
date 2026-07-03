#!/usr/bin/env python3
"""
extract_page_content.py — fetch pages and extract title/H1/headings/body text. Uses
trafilatura if installed (best), else a regex fallback. Caches to a directory.

Live network required.

Usage:
  python extract_page_content.py --urls urls.json --out-dir brands/<slug>/data/crawl
  python extract_page_content.py --url https://example.com/page --out-dir ./cache
"""
from __future__ import annotations
import argparse, json, os, re, hashlib, sys, urllib.request

UA = "SemanticSEOSuite/0.1 polite-crawler"

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def extract(url, html):
    title = (re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S) or [None, ""])[1].strip()
    h1s = [re.sub("<[^>]+>", "", h).strip() for h in re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)]
    headings = []
    for lvl in (2, 3):
        for h in re.findall(rf"<h{lvl}[^>]*>(.*?)</h{lvl}>", html, re.I | re.S):
            headings.append({"level": f"H{lvl}", "text": re.sub("<[^>]+>", "", h).strip()})
    body = ""
    try:
        import trafilatura
        body = trafilatura.extract(html) or ""
    except Exception:
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.I | re.S)
        text = re.sub("<[^>]+>", " ", text)
        body = re.sub(r"\s+", " ", text).strip()
    links = list({re.sub(r"#.*$", "", h) for h in re.findall(r'href=["\']([^"\']+)["\']', html)})
    return {"url": url, "title": title, "h1": h1s, "headings": headings,
            "body": body, "links": links, "provenance": "measured", "source": f"crawl:{url}"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls"); ap.add_argument("--url")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    targets = []
    if a.url: targets = [a.url]
    elif a.urls: targets = [u["url"] for u in json.load(open(a.urls))["urls"]]
    else: ap.error("provide --url or --urls")
    done = 0
    for url in targets:
        try:
            data = extract(url, fetch(url))
        except Exception as e:
            sys.stderr.write(f"[extract] skip {url}: {e}\n"); continue
        fn = hashlib.md5(url.encode()).hexdigest()[:16] + ".json"
        json.dump(data, open(os.path.join(a.out_dir, fn), "w"), indent=2)
        done += 1
    print(json.dumps({"extracted": done, "out_dir": a.out_dir}))

if __name__ == "__main__":
    main()
