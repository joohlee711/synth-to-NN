ARCHETYPES: list[str] = [
    "MLP",
    "CNN",
    "RNN_LSTM",
    "Transformer",
    "GAN",
    "VAE",
    "Diffusion",
    "MoE",
]

# function_id -> { archetype_name: weight }
# Calibrate with musician friends. Empty = matcher returns 0 for everything.
WEIGHTS: dict[int, dict[str, float]] = {
    # 3:  "LFO"                 e.g. {"RNN_LSTM": 1.0, "Transformer": 0.3}
    # 4:  "Envelope Generator"
    # 15: "CV Modulation"
    # 28: "Envelope Follower"
    # 29: "Attenuator"
    # 30: "Slew Limiter"
    # 37: "Logic"
    # 39: "Function Generator"
}


def archetype_vector(name: str) -> dict[int, float]:
    return {fid: w.get(name, 0.0) for fid, w in WEIGHTS.items()}
