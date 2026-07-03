#!/usr/bin/env python3
"""
embed_corpus.py — turn text (query networks, page content, node titles) into vectors.

Primary backend: sentence-transformers (a real embedding model, default all-MiniLM-L6-v2
or a Qwen3-Embedding variant from config). Requires the model to be downloadable once.

Fallback backend: a deterministic, dependency-free hashing embedding (bag-of-character-
n-grams into a fixed-dim vector, L2-normalised). It is NOT semantically strong, but it
is stable, offline, and good enough for coarse dedupe/lateral-link sanity checks when no
model is available (e.g. locked-down environments). Outputs are labelled with the
backend so downstream provenance stays honest: model-backed = 'derived(embedding:model)',
fallback = 'derived(embedding:hash-fallback)'.

Usage:
  # embed a JSON list of {"id":..., "text":...}
  python embed_corpus.py --in items.json --out vecs.npz [--model NAME] [--fallback]
  # or embed the query networks of a topical map directly
  python embed_corpus.py --map brands/<slug>/topical-map.json --out vecs.npz

Output: an .npz with arrays `ids` (str) and `vectors` (float32, n x d), plus a sidecar
.meta.json recording the backend + dim.
"""
from __future__ import annotations
import argparse, json, hashlib, math, os, sys

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FALLBACK_DIM = 512


def _load_items(args):
    if args.map:
        m = json.load(open(args.map))
        items = []
        for n in m["nodes"]:
            qs = [q["query"] for q in n.get("query_network", [])]
            text = n["title"] + " . " + " . ".join(qs)
            items.append({"id": n["id"], "text": text})
        return items
    return json.load(open(args.inp))


def _hash_embed(texts, dim=FALLBACK_DIM):
    """Deterministic char-3gram hashing embedding, L2-normalised. Offline, stable."""
    vecs = []
    for t in texts:
        v = [0.0] * dim
        s = f"  {t.lower()}  "
        for i in range(len(s) - 2):
            g = s[i:i + 3]
            h = int(hashlib.md5(g.encode()).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if (h >> 8) & 1 else -1.0
            v[idx] += sign
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        vecs.append([x / norm for x in v])
    return vecs, dim


def _model_embed(texts, model_name):
    from sentence_transformers import SentenceTransformer  # may trigger a download
    model = SentenceTransformer(model_name)
    arr = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return arr.tolist(), arr.shape[1]


def embed(items, model_name=DEFAULT_MODEL, force_fallback=False):
    texts = [it["text"] for it in items]
    ids = [it["id"] for it in items]
    backend = "hash-fallback"
    if not force_fallback:
        try:
            vecs, dim = _model_embed(texts, model_name)
            backend = f"model:{model_name}"
        except Exception as e:
            sys.stderr.write(f"[embed_corpus] model backend unavailable ({e.__class__.__name__}: {e}). "
                             f"Falling back to offline hashing embedding.\n")
            vecs, dim = _hash_embed(texts)
    else:
        vecs, dim = _hash_embed(texts)
    return ids, vecs, dim, backend


def save(out_path, ids, vecs, dim, backend):
    meta = {"backend": backend, "dim": dim, "count": len(ids),
            "provenance": "derived", "note": f"embedding:{backend}"}
    if out_path.endswith(".json"):
        json.dump({"ids": ids, "vectors": vecs}, open(out_path, "w"))
    else:
        try:
            import numpy as np
            np.savez(out_path, ids=np.array(ids), vectors=np.array(vecs, dtype="float32"))
            if not out_path.endswith(".npz"):
                out_path += ".npz"
        except Exception:
            out_path = out_path.rsplit(".", 1)[0] + ".json"
            json.dump({"ids": ids, "vectors": vecs}, open(out_path, "w"))
    json.dump(meta, open(out_path.rsplit(".", 1)[0] + ".meta.json", "w"), indent=2)
    return out_path, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp")
    ap.add_argument("--map")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--fallback", action="store_true", help="force offline hashing embedding")
    a = ap.parse_args()
    if not a.inp and not a.map:
        ap.error("provide --in items.json or --map topical-map.json")
    items = _load_items(a)
    ids, vecs, dim, backend = embed(items, a.model, a.fallback)
    path, meta = save(a.out, ids, vecs, dim, backend)
    print(json.dumps({"out": path, **meta}, indent=2))


if __name__ == "__main__":
    main()
