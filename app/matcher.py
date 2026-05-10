import math
from collections import Counter

from . import archetypes


def score_rack(function_ids: list[int]) -> list[tuple[str, float]]:
    rack_vec = Counter(function_ids)
    results = [
        (a, _cosine(rack_vec, archetypes.archetype_vector(a)))
        for a in archetypes.ARCHETYPES
    ]
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def _cosine(a, b) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
