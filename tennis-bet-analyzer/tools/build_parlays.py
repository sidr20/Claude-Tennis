"""Builds 2-pick and 3-pick parlay combinations from STRONG/MODERATE props.

Per project rules: top 2 two-pick combos, top 1 three-pick combo, fixed flat
stakes ($5 / $4 / $3 for those three slots), which caps total session spend
at $12 -- 60% of a $20 bankroll -- whenever all three slots are filled.
Correlated legs (same player, or two props from the same match) are skipped.
"""
import itertools

PAYOUTS = {2: 3.0, 3: 5.0}
ELIGIBLE_RATINGS = {"STRONG", "MODERATE"}

# (parlay size, slot index within that size, in EV order) -> flat stake
STAKE_SCHEDULE = {
    (2, 0): 5.0,
    (2, 1): 4.0,
    (3, 0): 3.0,
}
MAX_PER_SIZE = {2: 2, 3: 1}


def _shares_a_match(leg_a: dict, leg_b: dict) -> bool:
    a_people = {leg_a["player_name"], leg_a.get("opponent")} - {None}
    b_people = {leg_b["player_name"], leg_b.get("opponent")} - {None}
    return bool(a_people & b_people)


def build_parlays(evaluations: list, bankroll: float = 20.0) -> dict:
    candidates = [
        e for e in evaluations
        if e.get("rating") in ELIGIBLE_RATINGS and e.get("true_probability") is not None
    ]

    parlays_by_size = {}
    for size, payout in PAYOUTS.items():
        combos = []
        for combo in itertools.combinations(candidates, size):
            if any(_shares_a_match(a, b) for a, b in itertools.combinations(combo, 2)):
                continue  # correlated legs -- same player or same match

            combined_prob = 1.0
            for leg in combo:
                combined_prob *= leg["true_probability"]
            ev_per_dollar = combined_prob * payout - 1
            confidences = {leg.get("confidence", "medium") for leg in combo}
            combined_confidence = "HIGH" if confidences == {"high"} else "MEDIUM"

            combos.append({
                "legs": [
                    {
                        "player_name": leg["player_name"],
                        "prop": leg["raw_text"],
                        "true_probability": leg["true_probability"],
                    }
                    for leg in combo
                ],
                "combined_probability": round(combined_prob, 4),
                "combined_confidence": combined_confidence,
                "payout_multiplier": payout,
                "ev_per_dollar": round(ev_per_dollar, 4),
            })

        combos.sort(key=lambda c: c["ev_per_dollar"], reverse=True)
        top = [c for c in combos if c["ev_per_dollar"] > 0][:MAX_PER_SIZE[size]]
        for slot, combo in enumerate(top):
            combo["stake"] = STAKE_SCHEDULE[(size, slot)]
            combo["potential_payout"] = combo["stake"] * payout
        parlays_by_size[f"{size}_pick"] = top

    total_spend = sum(c["stake"] for combos in parlays_by_size.values() for c in combos)

    return {
        "parlays_by_size": parlays_by_size,
        "num_candidates": len(candidates),
        "total_spend": total_spend,
        "bankroll": bankroll,
    }
