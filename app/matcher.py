import math
from collections import Counter

from . import archetypes


def _norm(s: str) -> str:
    return s.strip().casefold()


def _idf_weights() -> dict[str, float]:
    """log(N/k) where N = total archetypes, k = archetypes containing the term.

    A tag exclusive to one archetype (k=1) is highly discriminative;
    a tag in many archetypes carries little ranking signal. A tag in
    every archetype gets IDF=0 (drops out).
    """
    k_counts: Counter = Counter()
    for arche in archetypes.ARCHETYPES:
        for fn in archetypes.archetype_vector(arche):
            k_counts[_norm(fn)] += 1
    n = len(archetypes.ARCHETYPES)
    return {term: math.log(n / k) for term, k in k_counts.items() if k > 0}


def score_rack(function_names: list[str]) -> dict:
    rack_norm_to_orig: dict[str, str] = {}
    for fn in function_names:
        rack_norm_to_orig.setdefault(_norm(fn), fn)
    raw_counts = Counter(_norm(fn) for fn in function_names)

    idf = _idf_weights()
    rack_vec = {
        term: math.log1p(c) * idf.get(term, 0.0)
        for term, c in raw_counts.items()
    }

    scores: list[dict] = []
    matched_norm: set[str] = set()
    for arche in archetypes.ARCHETYPES:
        a_orig = archetypes.archetype_vector(arche)
        a_vec = {
            _norm(k): v * idf.get(_norm(k), 0.0) for k, v in a_orig.items()
        }
        scores.append({"archetype": arche, "score": _cosine(rack_vec, a_vec)})
        matched_norm |= {t for t in raw_counts if t in {_norm(k) for k in a_orig}}

    scores.sort(key=lambda x: x["score"], reverse=True)
    function_counts = {rack_norm_to_orig[n]: c for n, c in raw_counts.items()}
    matched = sorted({rack_norm_to_orig[n] for n in matched_norm})
    unmatched = sorted(
        {rack_norm_to_orig[n] for n in raw_counts if n not in matched_norm}
    )
    return {
        "scores": scores,
        "function_counts": function_counts,
        "matched_functions": matched,
        "unmatched_functions": unmatched,
    }


def _cosine(a, b) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
