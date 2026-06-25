"""Compares estimated true probability against PrizePicks implied probability and rates the bet."""

DEFAULT_IMPLIED_PROB = 0.54

# Checked in order; first satisfied threshold wins. Falls through to "FADE"
# (true probability below the implied baseline).
RATING_THRESHOLDS = (
    (0.10, "STRONG"),
    (0.05, "MODERATE"),
    (0.0, "WEAK"),
)


def evaluate_edge(true_probability, implied: float = DEFAULT_IMPLIED_PROB) -> dict:
    if true_probability is None:
        return {
            "edge": None,
            "edge_pct": None,
            "rating": "FLAGGED - INSUFFICIENT DATA",
            "implied_probability": implied,
        }

    edge = true_probability - implied
    rating = "FADE"
    for threshold, label in RATING_THRESHOLDS:
        if edge >= threshold:
            rating = label
            break

    return {
        "edge": round(edge, 4),
        "edge_pct": round(edge * 100, 1),
        "rating": rating,
        "implied_probability": implied,
    }
