import json
from pathlib import Path

WEIGHTS_PATH = Path(__file__).resolve().parent / "weights.json"


def _load() -> dict:
    with open(WEIGHTS_PATH) as f:
        return json.load(f)


_data = _load()
ARCHETYPES: list[str] = list(_data["archetypes"])
WEIGHTS: dict[str, dict[str, float]] = dict(_data["weights"])


def archetype_vector(name: str) -> dict[str, float]:
    return dict(WEIGHTS.get(name, {}))


def reload() -> None:
    global _data, ARCHETYPES, WEIGHTS
    _data = _load()
    ARCHETYPES = list(_data["archetypes"])
    WEIGHTS = dict(_data["weights"])
