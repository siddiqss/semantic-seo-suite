#!/usr/bin/env python3
"""
build_skills.py — turn the shared-monorepo skills into self-contained skill folders
ready for .skill packaging (claude.ai / Skills API install).

Each skill in the monorepo references ../../framework/*.md and ../../scripts/*.py. For a
standalone .skill, those must live inside the skill folder. This script, per skill:
  1. reads SKILL.md, finds referenced framework docs + scripts,
  2. computes the transitive import closure of those scripts (+ provenance.py),
  3. copies framework docs -> <dist>/<skill>/references/,
     scripts -> <dist>/<skill>/scripts/,
  4. rewrites ../../framework/X.md -> references/X.md and ../../scripts/Y.py -> scripts/Y.py
     in the SKILL.md,
  5. copies evals/ (excluded from the final .skill by the packager, kept for the eval loop).

Run from repo root:  python scripts/build_skills.py --out dist
"""
from __future__ import annotations
import argparse, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMEWORK = os.path.join(ROOT, "framework")
SCRIPTS = os.path.join(ROOT, "scripts")

FW_REF = re.compile(r"\.\./\.\./framework/([A-Za-z0-9_\-]+\.md)")
SC_REF = re.compile(r"\.\./\.\./scripts/([A-Za-z0-9_\-]+\.py)")
LOCAL_IMPORT = re.compile(r"^(?:from|import)\s+([a-z0-9_]+)", re.MULTILINE)


def script_closure(seed_scripts):
    """Follow imports among our own scripts to gather every script a skill needs."""
    available = {f[:-3] for f in os.listdir(SCRIPTS) if f.endswith(".py")}
    needed, stack = set(), list(seed_scripts)
    while stack:
        name = stack.pop()
        mod = name[:-3] if name.endswith(".py") else name
        if mod not in available or mod in needed:
            continue
        needed.add(mod)
        src = open(os.path.join(SCRIPTS, mod + ".py")).read()
        for imp in LOCAL_IMPORT.findall(src):
            if imp in available and imp not in needed:
                stack.append(imp)
    needed.add("provenance")  # always ship the fabrication backbone
    return sorted(needed)


def build_one(skill_dir, out_root):
    name = os.path.basename(skill_dir.rstrip("/"))
    skill_md = open(os.path.join(skill_dir, "SKILL.md")).read()
    fw = sorted(set(FW_REF.findall(skill_md)))
    sc_seed = sorted(set(SC_REF.findall(skill_md)))
    scripts = script_closure(sc_seed)

    dest = os.path.join(out_root, name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(os.path.join(dest, "references"), exist_ok=True)
    os.makedirs(os.path.join(dest, "scripts"), exist_ok=True)

    for doc in fw:
        src = os.path.join(FRAMEWORK, doc)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(dest, "references", doc))
    # always include the overview so provenance rules travel with every skill
    if os.path.exists(os.path.join(FRAMEWORK, "00-overview.md")):
        shutil.copy(os.path.join(FRAMEWORK, "00-overview.md"),
                    os.path.join(dest, "references", "00-overview.md"))
    for s in scripts:
        shutil.copy(os.path.join(SCRIPTS, s + ".py"), os.path.join(dest, "scripts", s + ".py"))

    # rewrite paths in SKILL.md
    new_md = FW_REF.sub(r"references/\1", skill_md)
    new_md = SC_REF.sub(r"scripts/\1", new_md)
    open(os.path.join(dest, "SKILL.md"), "w").write(new_md)

    # carry evals along (packager excludes them from the final .skill)
    ev = os.path.join(skill_dir, "evals")
    if os.path.isdir(ev):
        shutil.copytree(ev, os.path.join(dest, "evals"))

    return name, fw, scripts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    a = ap.parse_args()
    out_root = os.path.join(ROOT, a.out)
    os.makedirs(out_root, exist_ok=True)
    skills_dir = os.path.join(ROOT, "skills")
    built = []
    for name in sorted(os.listdir(skills_dir)):
        sd = os.path.join(skills_dir, name)
        if os.path.isdir(sd) and os.path.exists(os.path.join(sd, "SKILL.md")):
            built.append(build_one(sd, out_root))
    for name, fw, sc in built:
        print(f"{name}: {len(fw)} framework refs, {len(sc)} scripts")
    print(f"\nStaged {len(built)} skills under {out_root}/")


if __name__ == "__main__":
    main()
