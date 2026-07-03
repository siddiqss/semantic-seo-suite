#!/usr/bin/env python3
"""
cluster_keywords.py — group queries/nodes by embedding similarity and suggest merges.

Used by topical-map-builder to dedupe the raw map (cannibalization prevention at design
time). Simple, dependency-light agglomerative (single-link) clustering at a cosine
distance threshold. Reads an embed_corpus .npz/.json.

Usage:
  python cluster_keywords.py --vecs vecs.npz --threshold 0.86
Output: clusters (each a list of ids) + suggested merges for multi-id clusters.
Everything is `derived`; signal strength inherits the embedding backend.
"""
from __future__ import annotations
import argparse, json, sys
from semantic_distance import load_vecs, cosine


def cluster(ids, vecs, threshold):
    n = len(ids)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(n):
        for j in range(i + 1, n):
            if cosine(vecs[i], vecs[j]) >= threshold:
                union(i, j)

    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(ids[i])
    return list(groups.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vecs", required=True)
    ap.add_argument("--threshold", type=float, default=0.86)
    a = ap.parse_args()
    ids, vecs, meta = load_vecs(a.vecs)
    clusters = cluster(ids, vecs, a.threshold)
    merges = [c for c in clusters if len(c) > 1]
    res = {
        "backend": meta.get("backend", "unknown"),
        "threshold": a.threshold,
        "n_clusters": len(clusters),
        "clusters": clusters,
        "suggested_merges": merges,
        "note": "Members of a suggested_merge share intent+queries closely enough to "
                "cannibalize; merge them or re-scope one to a distinct intent.",
    }
    print(json.dumps(res, indent=2))
    if meta.get("backend", "").startswith("hash-fallback"):
        sys.stderr.write("[cluster_keywords] NOTE: hash-fallback embeddings — coarse.\n")


if __name__ == "__main__":
    main()
