#!/usr/bin/env python3
"""Single entry point for the tennis prop betting analyzer (WAT framework).

Run with: python agent.py

This script drives the conversation: it prompts for props, parses them, then
for each prop prints the exact WebSearch queries needed and pauses for the
orchestrating agent (Claude, via its own WebSearch tool -- never an external
search API) to paste back structured findings. Once every prop is researched,
it runs the deterministic pipeline (estimate -> edge -> parlays) and prints
the final report. See workflows/analyze_props.md for the full SOP.
"""
import json
from datetime import date
from pathlib import Path

from tools import build_parlays, estimate_probability, evaluate_edge, parse_input, print_report, research_player, track_results
from tools.parse_input import STAT_DISPLAY_NAMES

ROOT = Path(__file__).parent
RESEARCH_DIR = ROOT / ".tmp" / "research"

STAT_QUERY_HINTS = {
    "aces": "average aces per match on their current surface, recent ace counts",
    "double_faults": "double-fault tendencies on their current surface",
    "games_won": "average games won per match recently",
    "first_serve_pct": "recent first-serve percentage trends",
}

RATING_RANK = {"STRONG": 3, "MODERATE": 2, "WEAK": 1, "FADE": 0}


def _read_multiline(prompt: str) -> str:
    print(prompt)
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


def _read_json_block(prompt: str) -> dict:
    print(prompt)
    print("(Paste JSON -- one line or several. Finish with a blank line. "
          "Type INCONCLUSIVE if the research turned up nothing usable.)")
    lines = []
    while True:
        line = input()
        stripped = line.strip()
        if stripped.upper() == "INCONCLUSIVE":
            return {"inconclusive": True, "notes": "Research inconclusive -- flagged by agent."}
        if stripped == "":
            break
        lines.append(line)
    return json.loads("\n".join(lines))


def collect_props() -> list:
    raw = _read_multiline(
        "Enter your PrizePicks tennis props, one per line "
        "(e.g. \"Carlos Alcaraz Aces Over 8.5\", or just \"Carlos Alcaraz Aces 8.5\" "
        "to have both sides evaluated). Press Enter on a blank line when done:"
    )
    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]

    props = []
    for idx, line in enumerate(lines):
        prop = parse_input.parse_line(line, idx)
        while not prop["parse_ok"]:
            print(f"\nCould not parse: \"{prop['raw_text']}\"")
            retry = input("Re-enter this prop (format: Player StatType Over/Under Line), or type SKIP: ").strip()
            if retry.upper() == "SKIP":
                prop = None
                break
            prop = parse_input.parse_line(retry, idx)
        if prop:
            props.append(prop)
    return props


def research_props(props: list) -> None:
    for prop in props:
        print(f"\n{'-' * 60}")
        print(f"RESEARCH NEEDED: {prop['player_name']} -- {prop['raw_text']}")
        stat_hint = STAT_QUERY_HINTS.get(prop["stat_type"], "the relevant stat")
        print("Run WebSearch for:")
        print(f"  1. {prop['player_name']} last 5 matches -- results, surface, current tournament/round")
        print(f"  2. {prop['player_name']} {stat_hint}")
        print(f"  3. {prop['player_name']} head-to-head vs today's opponent (if known)")
        print(f"  4. {prop['player_name']} injury news, withdrawals, fatigue")
        print("Then synthesize findings into JSON per workflows/research_player.md.")
        findings = _read_json_block(f"\nFindings for {prop['id']}:")
        research_player.save_research(prop["id"], findings, RESEARCH_DIR)


def _evaluate_prop(prop: dict, findings: dict, implied: float) -> dict:
    estimate = estimate_probability.estimate_probability(prop, findings)

    if estimate.get("insufficient_data") or estimate.get("true_probability_over") is None:
        edge = evaluate_edge.evaluate_edge(None, implied=implied)
        return {**prop, **findings, **estimate, **edge}

    if prop.get("direction") in ("over", "under"):
        edge = evaluate_edge.evaluate_edge(estimate["true_probability"], implied=implied)
        return {**prop, **findings, **estimate, **edge}

    # Undirected prop -- evaluate both sides, recommend whichever has the better edge.
    edge_over = evaluate_edge.evaluate_edge(estimate["true_probability_over"], implied=implied)
    edge_under = evaluate_edge.evaluate_edge(estimate["true_probability_under"], implied=implied)

    if RATING_RANK[edge_over["rating"]] >= RATING_RANK[edge_under["rating"]]:
        best_direction, best_probability, best_edge = "over", estimate["true_probability_over"], edge_over
        other_direction, other_probability, other_edge = "under", estimate["true_probability_under"], edge_under
    else:
        best_direction, best_probability, best_edge = "under", estimate["true_probability_under"], edge_under
        other_direction, other_probability, other_edge = "over", estimate["true_probability_over"], edge_over

    stat_label = STAT_DISPLAY_NAMES.get(prop["stat_type"], prop["stat_type"])
    return {
        **prop,
        **findings,
        **estimate,
        **best_edge,
        "direction": best_direction,
        "true_probability": best_probability,
        "raw_text": f"{prop['player_name']} {stat_label} {best_direction.title()} {prop['line_value']}",
        "other_side": {
            "direction": other_direction,
            "true_probability": other_probability,
            **other_edge,
        },
    }


def run_pipeline(props: list, bankroll: float = 20.0, implied: float = 0.54) -> list:
    evaluations = []
    for prop in props:
        findings = research_player.load_research(prop["id"], RESEARCH_DIR)
        evaluations.append(_evaluate_prop(prop, findings, implied))

    parlays = build_parlays.build_parlays(evaluations, bankroll=bankroll)
    print_report.print_report(evaluations, parlays, bankroll=bankroll, report_date=date.today().isoformat())
    return evaluations


def resolve_pending_results() -> None:
    pending = track_results.pending_entries()
    if not pending:
        return

    print(f"\n{'-' * 60}")
    print(f"{len(pending)} prop(s) are awaiting a real-world result:")
    for entry in pending:
        print(
            f"\n{entry['raw_text']}  "
            f"(predicted {entry['true_probability'] * 100:.1f}%, {entry['rating']}, logged {entry['date_logged']})"
        )
        answer = input(
            "Enter the actual stat value, or SKIP (not final yet), or VOID (match didn't happen/no contest): "
        ).strip()
        if answer == "" or answer.upper() == "SKIP":
            continue
        if answer.upper() == "VOID":
            track_results.void_entry(entry["log_id"], reason="Marked void by user")
            print("Marked void -- excluded from calibration.")
            continue
        try:
            actual_value = float(answer)
        except ValueError:
            print("Couldn't parse that as a number -- leaving it pending.")
            continue
        result = track_results.resolve_entry(entry["log_id"], actual_value)
        print(f"Logged: actual {actual_value} -> {'HIT' if result['hit'] else 'MISS'}")


def print_calibration_check() -> None:
    report = track_results.calibration_report()
    if report["overall"]["n"] == 0:
        return

    print(f"\n{'=' * 60}")
    print("CALIBRATION CHECK (all-time, resolved props)")
    print("=" * 60)
    for rating in ("STRONG", "MODERATE", "WEAK", "FADE"):
        b = report["by_rating"].get(rating)
        if not b:
            continue
        print(
            f"{rating}: {b['n']} resolved -- actual hit rate {b['hit_rate'] * 100:.1f}% "
            f"vs. avg predicted {b['avg_predicted_probability'] * 100:.1f}%"
        )
    overall = report["overall"]
    print(f"\nOverall: {overall['n']} resolved, {overall['hit_rate'] * 100:.1f}% hit rate")


def main():
    print("=" * 60)
    print("TENNIS PROP BETTING ANALYZER".center(60))
    print("=" * 60)

    resolve_pending_results()

    props = collect_props()
    if not props:
        print("\nNo new props entered.")
    else:
        research_props(props)
        evaluations = run_pipeline(props)
        added = track_results.log_new_evaluations(evaluations)
        if added:
            print(f"\nLogged {added} new prediction(s) to results_log.json for future calibration tracking.")

    print_calibration_check()


if __name__ == "__main__":
    main()
