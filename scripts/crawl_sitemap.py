#!/usr/bin/env python3
"""
crawl_sitemap.py — discover a site's URLs via sitemap.xml, with a shallow same-domain
BFS fallback. Respects robots.txt, caps pages/depth, polite delays. Output: JSON list
of {url, source} to stdout or --out.

Live network required (runs on your machine, not in the locked sandbox).

Usage:
  python crawl_sitemap.py --domain example.com [--max-pages 500] [--max-depth 3] [--out urls.json]
"""
from __future__ import annotations
import argparse, json, sys, time, urllib.parse, urllib.request, urllib.robotparser
import re

UA = "SemanticSEOSuite/0.1 (+https://localhost) polite-crawler"

def _get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def from_sitemap(domain):
    base = f"https://{domain}"
    urls = []
    for sm in (f"{base}/sitemap.xml", f"{base}/sitemap_index.xml"):
        try:
            xml = _get(sm)
        except Exception:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
        # if it's an index, recurse one level into child sitemaps
        child_sitemaps = [u for u in locs if u.endswith(".xml")]
        page_urls = [u for u in locs if not u.endswith(".xml")]
        urls.extend({"url": u, "source": "sitemap"} for u in page_urls)
        for cs in child_sitemaps[:50]:
            try:
                cxml = _get(cs)
                urls.extend({"url": u, "source": "sitemap"} for u in
                            re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", cxml) if not u.endswith(".xml"))
            except Exception:
                pass
        if urls:
            break
    return urls

def bfs(domain, max_pages, max_depth, delay=0.5):
    base = f"https://{domain}"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(f"{base}/robots.txt"); rp.read()
    except Exception:
        rp = None
    seen, out, queue = set(), [], [(base, 0)]
    while queue and len(out) < max_pages:
        url, depth = queue.pop(0)
        if url in seen or depth > max_depth:
            continue
        seen.add(url)
        if rp and not rp.can_fetch(UA, url):
            continue
        try:
            html = _get(url); time.sleep(delay)
        except Exception:
            continue
        out.append({"url": url, "source": "bfs"})
        if depth < max_depth:
            for href in re.findall(r'href=["\']([^"\']+)["\']', html):
                nxt = urllib.parse.urljoin(url, href).split("#")[0]
                if urllib.parse.urlparse(nxt).netloc.endswith(domain) and nxt not in seen:
                    queue.append((nxt, depth + 1))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True)
    ap.add_argument("--max-pages", type=int, default=500)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args()
    urls = from_sitemap(a.domain)
    if not urls:
        sys.stderr.write("[crawl_sitemap] no sitemap found; falling back to BFS crawl.\n")
        urls = bfs(a.domain, a.max_pages, a.max_depth)
    urls = urls[:a.max_pages]
    payload = {"domain": a.domain, "count": len(urls), "urls": urls,
               "provenance": "measured", "source": "crawl"}
    (open(a.out, "w") if a.out else sys.stdout).write(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
