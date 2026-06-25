"""Estimates the true probability a prop hits using a weighted scoring model.

Components and weights (per workflows/research_player.md):
- Stat hit rate from recent matches (computed here from raw values): 40%
- Surface-specific tendency (agent-estimated probability):            25%
- Opponent factor (agent-estimated probability):                      20%
- Injury/fatigue/momentum (agent-estimated probability):               15%

When research confidence is medium or low, the weighted estimate is shrunk
toward a neutral 50% -- a conservative adjustment for limited or conflicting
data, rather than trusting a thin sample at full strength.

The model always computes the Over-side probability first, then derives
Under as 1 - Over (valid for PrizePicks' half-point lines, which never tie).
If the prop specifies a direction, only that side is returned as
`true_probability`. If not, both `true_probability_over` and
`true_probability_under` are returned so the caller can pick the better edge.
"""

WEIGHTS = {
    "stat_hit_rate": 0.40,
    "surface_probability": 0.25,
    "opponent_probability": 0.20,
    "momentum_probability": 0.15,
}

CONFIDENCE_SHRINK = {"high": 0.0, "medium": 0.25, "low": 0.5}


def _hit_rate_over(values, line):
    if not values:
        return None
    real_values = [v for v in values if v is not None]
    if not real_values:
        return None
    return sum(1 for v in real_values if v > line) / len(real_values)


def estimate_probability(prop: dict, findings: dict) -> dict:
    if findings.get("inconclusive"):
        return {
            "true_probability": None,
            "true_probability_over": None,
            "true_probability_under": None,
            "insufficient_data": True,
            "model_notes": findings.get("notes") or "Research inconclusive -- not guessing a probability.",
        }

    hit_rate_over = _hit_rate_over(findings.get("recent_match_values"), prop["line_value"])
    if hit_rate_over is None:
        return {
            "true_probability": None,
            "true_probability_over": None,
            "true_probability_under": None,
            "insufficient_data": True,
            "model_notes": findings.get("notes") or "No recent match values found for this stat -- not guessing.",
        }

    components = {
        "stat_hit_rate": hit_rate_over,
        "surface_probability": findings.get("surface_probability", 0.5),
        "opponent_probability": findings.get("opponent_probability", 0.5),
        "momentum_probability": findings.get("momentum_probability", 0.5),
    }
    weighted = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)

    shrink = CONFIDENCE_SHRINK.get(findings.get("confidence", "medium"), 0.25)
    true_probability_over = weighted * (1 - shrink) + 0.5 * shrink
    true_probability_under = 1 - true_probability_over

    direction = prop.get("direction")
    if direction == "over":
        true_probability = true_probability_over
    elif direction == "under":
        true_probability = true_probability_under
    else:
        true_probability = None  # undirected -- caller picks a side from the two values below

    return {
        "true_probability": round(true_probability, 4) if true_probability is not None else None,
        "true_probability_over": round(true_probability_over, 4),
        "true_probability_under": round(true_probability_under, 4),
        "insufficient_data": False,
        "stat_hit_rate": round(hit_rate_over, 4),
        "components": {k: round(v, 4) for k, v in components.items()},
        "confidence_shrink_applied": shrink,
        "model_notes": findings.get("notes", ""),
    }
