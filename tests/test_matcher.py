from app import archetypes, matcher


def test_archetypes_loaded():
    assert len(archetypes.ARCHETYPES) == 8
    assert "MLP" in archetypes.ARCHETYPES
    assert all(archetypes.archetype_vector(a) for a in archetypes.ARCHETYPES)


def test_score_classic_chain_picks_mlp():
    rack = ["VCO", "Filter", "VCA", "Envelope Generator", "Mixer"]
    result = matcher.score_rack(rack)
    assert result["scores"][0]["archetype"] == "MLP"
    assert result["scores"][0]["score"] > 0


def test_score_sequencer_heavy_picks_cnn():
    rack = ["Sequencer", "Sequencer", "Clock Modulator", "Quantizer", "Drum"]
    result = matcher.score_rack(rack)
    assert result["scores"][0]["archetype"] == "CNN"


def test_score_normalization_is_case_insensitive():
    a = matcher.score_rack(["VCO", "Filter", "VCA"])
    b = matcher.score_rack(["vco", "FILTER", "  vca  "])
    a_top = {s["archetype"]: s["score"] for s in a["scores"]}
    b_top = {s["archetype"]: s["score"] for s in b["scores"]}
    assert a_top == b_top


def test_unmatched_diagnostic():
    result = matcher.score_rack(["VCO", "Filter", "MadeUpFunction"])
    assert "MadeUpFunction" in result["unmatched_functions"]
    assert "VCO" in result["matched_functions"]


def test_empty_rack_safe():
    result = matcher.score_rack([])
    assert all(s["score"] == 0.0 for s in result["scores"])
    assert result["matched_functions"] == []
    assert result["unmatched_functions"] == []


def test_maths_only_rack():
    maths_funcs = [
        "LFO",
        "Envelope Generator",
        "CV Modulation",
        "Envelope Follower",
        "Attenuator",
        "Slew Limiter",
        "Logic",
        "Function Generator",
    ]
    result = matcher.score_rack(maths_funcs)
    top = result["scores"][0]
    assert top["archetype"] == "Transformer"
    assert top["score"] > 0
    second = result["scores"][1]
    assert second["score"] < top["score"]
