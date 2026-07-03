#!/usr/bin/env python3
"""
semantic_distance.py — cosine similarity utilities over an embedded corpus.

Reads an .npz (or .json fallback) produced by embed_corpus.py and provides:
  pairs      : all pairs above a similarity threshold (cannibalization / lateral-link)
  neighbors  : k nearest neighbours for one id
  centroid   : centroid vector + each id's distance from it (entity-drift signal)

All outputs are `derived` (they are computed from embeddings); the strength of the
signal inherits the embedding backend (model vs hash-fallback) — carry that note.

Usage:
  python semantic_distance.py pairs --vecs vecs.npz --threshold 0.86
  python semantic_distance.py neighbors --vecs vecs.npz --id n-013 --k 5
  python semantic_distance.py centroid --vecs vecs.npz
"""
from __future__ import annotations
import argparse, json, math, sys


def load_vecs(path):
    meta = {}
    mpath = path.rsplit(".", 1)[0] + ".meta.json"
    try:
        meta = json.load(open(mpath))
    except OSError:
        pass
    if path.endswith(".json"):
        d = json.load(open(path))
        return d["ids"], d["vectors"], meta
    import numpy as np
    z = np.load(path, allow_pickle=True)
    return list(map(str, z["ids"])), z["vectors"].tolist(), meta


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cosine(a, b):
    # vectors are L2-normalised by embed_corpus, so cosine == dot; guard anyway
    na = math.sqrt(dot(a, a)) or 1.0
    nb = math.sqrt(dot(b, b)) or 1.0
    return dot(a, b) / (na * nb)


def pairs(ids, vecs, threshold):
    out = []
    n = len(ids)
    for i in range(n):
        for j in range(i + 1, n):
            s = cosine(vecs[i], vecs[j])
            if s >= threshold:
                out.append({"a": ids[i], "b": ids[j], "similarity": round(s, 4),
                            "provenance": "derived"})
    out.sort(key=lambda x: -x["similarity"])
    return out


def neighbors(ids, vecs, target, k):
    if target not in ids:
        raise SystemExit(f"id {target} not in corpus")
    ti = ids.index(target)
    sims = [(ids[j], cosine(vecs[ti], vecs[j])) for j in range(len(ids)) if j != ti]
    sims.sort(key=lambda x: -x[1])
    return [{"id": i, "similarity": round(s, 4), "provenance": "derived"} for i, s in sims[:k]]


def centroid(ids, vecs):
    d = len(vecs[0])
    c = [sum(v[k] for v in vecs) / len(vecs) for k in range(d)]
    norm = math.sqrt(dot(c, c)) or 1.0
    c = [x / norm for x in c]
    dists = [{"id": ids[i], "distance_from_center": round(1 - cosine(vecs[i], c), 4),
              "provenance": "derived"} for i in range(len(ids))]
    dists.sort(key=lambda x: -x["distance_from_center"])
    return {"centroid_dim": d, "farthest_first": dists}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pairs", "neighbors", "centroid"])
    ap.add_argument("--vecs", required=True)
    ap.add_argument("--threshold", type=float, default=0.86)
    ap.add_argument("--id")
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()
    ids, vecs, meta = load_vecs(a.vecs)
    backend = meta.get("backend", "unknown")
    if a.cmd == "pairs":
        res = {"backend": backend, "threshold": a.threshold, "pairs": pairs(ids, vecs, a.threshold)}
    elif a.cmd == "neighbors":
        res = {"backend": backend, "id": a.id, "neighbors": neighbors(ids, vecs, a.id, a.k)}
    else:
        res = {"backend": backend, **centroid(ids, vecs)}
    print(json.dumps(res, indent=2))
    if backend.startswith("hash-fallback"):
        sys.stderr.write("[semantic_distance] NOTE: hash-fallback embeddings — treat "
                         "similarities as coarse; re-run with a model backend for decisions.\n")


if __name__ == "__main__":
    main()
