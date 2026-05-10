import math
from collections import Counter

from . import archetypes


def _norm(s: str) -> str:
    return s.strip().casefold()


def score_rack(function_names: list[str]) -> dict:
    rack_norm_to_orig: dict[str, str] = {}
    for n in function_names:
        rack_norm_to_orig.setdefault(_norm(n), n)
    rack_vec = Counter(_norm(n) for n in function_names)

    scores: list[dict] = []
    matched_norm: set[str] = set()
    for arche in archetypes.ARCHETYPES:
        a_orig = archetypes.archetype_vector(arche)
        a_vec = {_norm(k): v for k, v in a_orig.items()}
        scores.append({"archetype": arche, "score": _cosine(rack_vec, a_vec)})
        matched_norm |= set(rack_vec) & set(a_vec)

    scores.sort(key=lambda x: x["score"], reverse=True)
    function_counts = {rack_norm_to_orig[n]: c for n, c in rack_vec.items()}
    matched = sorted({rack_norm_to_orig[n] for n in matched_norm})
    unmatched = sorted(
        {rack_norm_to_orig[n] for n in rack_vec if n not in matched_norm}
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
