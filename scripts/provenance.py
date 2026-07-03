"""
provenance.py — the anti-fabrication backbone of the Semantic SEO Suite.

Every factual value that flows through the suite carries a provenance label so
that no output can silently present an invented number as a measured one. This
is the SEO analogue of a product attribute-lock validator: the point
is not to be pedantic, it is to make fabrication structurally visible.

Three provenance kinds, in decreasing order of trust:

    measured  - obtained from an external source of truth (an API, a crawl of a
                real page, Google Search Console, DataForSEO, Wikidata). Always
                carries a `source` string.
    derived   - computed deterministically from measured inputs (e.g. a centroid
                distance from real embeddings, a rollup of real GSC clicks).
                Carries the ids/sources of its inputs.
    asserted  - the model's judgement with no external grounding (e.g. an intent
                guessed from a query at tier T0). Legitimate and often useful,
                but must never be dressed up as measured.

A value with no provenance is a bug. Helpers here make the correct thing the
easy thing.

Usage:
    from provenance import measured, derived, asserted, is_grounded, strip

    vol = measured(1300, source="dataforseo:search_volume")
    dist = derived(0.82, inputs=["embeddings/page_014", "embeddings/centroid"])
    intent = asserted("informational", note="inferred from query shape, no SERP")

    if is_grounded(vol):   # measured or derived, not asserted
        ...

Each helper returns a plain dict so values are JSON-serialisable and can be
written straight into entity-profile.json / topical-map.json etc.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable

MEASURED = "measured"
DERIVED = "derived"
ASSERTED = "asserted"

VALID_KINDS = (MEASURED, DERIVED, ASSERTED)


def measured(value: Any, *, source: str, observed: str | None = None) -> dict:
    """A value obtained from an external source of truth.

    source: a machine-readable origin, e.g. "gsc:clicks", "crawl:https://x/p",
            "wikidata:Q1234", "dataforseo:search_volume".
    observed: ISO date the value was obtained (defaults to today).
    """
    if not source:
        raise ValueError("measured() requires a non-empty source")
    return {
        "value": value,
        "provenance": MEASURED,
        "source": source,
        "observed": observed or date.today().isoformat(),
    }


def derived(value: Any, *, inputs: Iterable[str], method: str | None = None) -> dict:
    """A value computed deterministically from measured/derived inputs.

    inputs: ids or sources of the things this was computed from.
    method: optional short description of the computation, e.g. "cosine_centroid".
    """
    inputs = list(inputs)
    if not inputs:
        raise ValueError("derived() requires at least one input reference")
    return {
        "value": value,
        "provenance": DERIVED,
        "inputs": inputs,
        "method": method,
    }


def asserted(value: Any, *, note: str | None = None) -> dict:
    """A model judgement with no external grounding. Honest guesswork.

    note: why the model believes this / what it would take to ground it.
    """
    return {
        "value": value,
        "provenance": ASSERTED,
        "note": note,
    }


def is_grounded(v: dict) -> bool:
    """True if the value is measured or derived (i.e. not pure assertion)."""
    return isinstance(v, dict) and v.get("provenance") in (MEASURED, DERIVED)


def kind_of(v: Any) -> str | None:
    """Return the provenance kind of a value, or None if it carries none."""
    if isinstance(v, dict):
        k = v.get("provenance")
        if k in VALID_KINDS:
            return k
    return None


def strip(v: Any) -> Any:
    """Return the bare value, dropping provenance metadata. Use only at the very
    edge (e.g. rendering) — never store stripped values back into state."""
    if isinstance(v, dict) and "value" in v and v.get("provenance") in VALID_KINDS:
        return v["value"]
    return v


def worst(values: Iterable[dict]) -> str:
    """Given several provenance-tagged values, return the weakest kind present.
    Useful when a derived figure depends on a mix of inputs: if any input was
    asserted, the result should not claim to be more than asserted."""
    order = {MEASURED: 3, DERIVED: 2, ASSERTED: 1}
    kinds = [kind_of(v) for v in values]
    kinds = [k for k in kinds if k]
    if not kinds:
        return ASSERTED
    return min(kinds, key=lambda k: order[k])


def audit(obj: Any, path: str = "$") -> list[str]:
    """Walk a nested dict/list and report any leaf that looks like a factual
    value but carries no provenance. Returns a list of human-readable findings.
    Skills and the validator use this to enforce X-01 (no naked numbers)."""
    findings: list[str] = []

    def looks_factual(key: str, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            return False
        if isinstance(value, bool):
            return False
        # Structural/counter fields that are legitimately bare integers.
        allow = {"id", "tier_level", "count", "index", "depth", "seq", "day_number"}
        return key.lower() not in allow

    def walk(node: Any, p: str) -> None:
        if isinstance(node, dict):
            if node.get("provenance") in VALID_KINDS:
                return  # a properly-tagged value; do not descend into it
            for k, val in node.items():
                if looks_factual(str(k), val):
                    findings.append(
                        f"{p}.{k} = {val!r} is a bare numeric value with no provenance"
                    )
                walk(val, f"{p}.{k}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{p}[{i}]")

    walk(obj, path)
    return findings


if __name__ == "__main__":
    # tiny self-test
    demo = {
        "volume": measured(1300, source="dataforseo:search_volume"),
        "distance": derived(0.82, inputs=["a", "b"], method="cosine"),
        "intent": asserted("informational", note="query shape only"),
        "bad": {"score": 0.97},  # should be flagged
        "id": 14,  # allowed bare
    }
    assert is_grounded(demo["volume"])
    assert not is_grounded(demo["intent"])
    assert worst([demo["volume"], demo["intent"]]) == ASSERTED
    problems = audit(demo)
    assert any("bad.score" in f for f in problems), problems
    print("provenance.py self-test passed. Findings:", problems)
