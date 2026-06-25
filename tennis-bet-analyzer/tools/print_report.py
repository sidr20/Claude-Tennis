"""Formats and prints the full prop analysis + parlay recommendations to the
terminal, matching the exact layout in workflows/build_report.md.
"""
from datetime import date

DIVIDER = "=" * 60

STAT_LABELS = {
    "aces": "ACES",
    "double_faults": "DOUBLE FAULTS",
    "games_won": "GAMES WON",
    "first_serve_pct": "FIRST SERVE %",
}

VERDICT_LABELS = {
    "STRONG": "STRONG ✅",
    "MODERATE": "MODERATE \U0001F7E1",
    "WEAK": "WEAK ⚠️",
    "FADE": "FADE ❌",
}


def print_report(evaluations: list, parlays: dict, bankroll: float = 20.0, report_date: str = None) -> None:
    report_date = report_date or date.today().isoformat()

    print(f"TENNIS PROP ANALYSIS — {report_date}")
    print(f"\nBankroll: ${bankroll:.0f}")

    strong = moderate = fade_avoid = 0

    for e in evaluations:
        stat_label = STAT_LABELS.get(e.get("stat_type"), (e.get("stat_type") or "UNKNOWN").upper())
        direction = (e.get("direction") or "?").upper()
        line_value = e.get("line_value")

        print(f"\n{e['player_name'].upper()} — {stat_label} — {direction} {line_value}")
        print(f"Surface: {e.get('surface', 'Unknown')}")
        print(f"Tournament: {e.get('tournament', 'Unknown')}")
        print(f"Recent Form: {e.get('recent_form_summary') or 'Not found'}")
        print(f"Stat Trend: {e.get('stat_trend_summary') or 'Not found'}")
        print(f"Opponent Factor: {e.get('opponent_factor_summary') or 'Unknown'}")
        print(f"Injury/News: {e.get('injury_news') or 'None found'}")

        if e.get("true_probability") is None:
            print("Estimated True Probability: INSUFFICIENT DATA")
            print(f"PrizePicks Implied Probability: {e.get('implied_probability', 0.54) * 100:.0f}%")
            print("Edge: N/A")
            print("Verdict: FLAGGED ⚠️")
            print(f"Reasoning: {e.get('model_notes') or 'Research inconclusive.'}")
            fade_avoid += 1
        else:
            print(f"Estimated True Probability: {e['true_probability'] * 100:.1f}%")
            print(f"PrizePicks Implied Probability: {e['implied_probability'] * 100:.0f}%")
            print(f"Edge: {e['edge_pct']:+.1f}%")
            print(f"Verdict: {VERDICT_LABELS.get(e['rating'], e['rating'])}")
            print(f"Reasoning: {e.get('model_notes') or ''}")
            other = e.get("other_side")
            if other:
                print(
                    f"Other Side ({other['direction'].title()} {line_value}): "
                    f"{other['true_probability'] * 100:.1f}% "
                    f"(edge {other['edge_pct']:+.1f}%, {other['rating']})"
                )
            if e["rating"] == "STRONG":
                strong += 1
            elif e["rating"] == "MODERATE":
                moderate += 1
            else:
                fade_avoid += 1

        print(DIVIDER)

    print("\nPARLAY RECOMMENDATIONS")

    two_picks = parlays["parlays_by_size"].get("2_pick", [])
    three_picks = parlays["parlays_by_size"].get("3_pick", [])

    print("\n2-PICK PARLAYS (3x payout):")
    if not two_picks:
        print("  None -- no 2-pick combo currently clears a positive expected value.")
    for combo in two_picks:
        legs_desc = " + ".join(leg["prop"] for leg in combo["legs"])
        print(f"\n→ {legs_desc}")
        print(f"   Combined confidence: {combo['combined_confidence']}")
        print(f"   Recommended stake: ${combo['stake']:.0f}")
        print(f"   Potential payout: ${combo['potential_payout']:.0f}")

    print("\n3-PICK PARLAYS (5x payout):")
    if not three_picks:
        print("  None -- no 3-pick combo currently clears a positive expected value.")
    for combo in three_picks:
        legs_desc = " + ".join(leg["prop"] for leg in combo["legs"])
        print(f"\n→ {legs_desc}")
        print(f"   Combined confidence: {combo['combined_confidence']}")
        print(f"   Recommended stake: ${combo['stake']:.0f}")
        print(f"   Potential payout: ${combo['potential_payout']:.0f}")

    if parlays["num_candidates"] < 2:
        print(
            f"\nOnly {parlays['num_candidates']} STRONG/MODERATE prop(s) found -- "
            f"need at least 2 for a parlay. No parlays recommended this session."
        )

    print(f"\n{DIVIDER}")
    print("SUMMARY")
    print(f"Strong plays: {strong}")
    print(f"Moderate plays: {moderate}")
    print(f"Fade/Avoid: {fade_avoid}")
    print(f"Total recommended spend: ${parlays['total_spend']:.0f} of ${bankroll:.0f} bankroll")
    print(DIVIDER)
    print("\nThis is probability-based analysis for informational purposes only.")
    print("Not financial advice. No outcome is guaranteed.")
