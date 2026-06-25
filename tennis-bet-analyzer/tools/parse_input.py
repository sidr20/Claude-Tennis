"""Parses raw PrizePicks tennis prop text into structured prop dicts.

Expected line format: "<Player> <Stat Type> [Over/Under] <Line>"
e.g. "Carlos Alcaraz Aces Over 8.5" or just "Carlos Alcaraz Aces 8.5"
(direction is optional -- PrizePicks doesn't fix a side, so omitting it tells
the pipeline to evaluate both Over and Under and recommend whichever clears
the edge -- see estimate_probability.py).
"""
import json
import re
import sys

STAT_PATTERNS = [
    (r"first serve %|first serve percentage|fs%", "first_serve_pct"),
    (r"double faults?|\bdfs?\b", "double_faults"),
    (r"\baces?\b", "aces"),
    (r"games won|total games|\bgames\b", "games_won"),
]

STAT_DISPLAY_NAMES = {
    "aces": "Aces",
    "double_faults": "Double Faults",
    "games_won": "Games Won",
    "first_serve_pct": "First Serve %",
}

DIRECTION_PATTERN = r"\b(over|under|o|u)\b"
LINE_VALUE_PATTERN = r"(\d+\.?\d*)"


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "unknown"


def parse_props(raw_text: str) -> list:
    lines = [l.strip() for l in raw_text.strip().splitlines() if l.strip()]
    return [parse_line(line, idx) for idx, line in enumerate(lines)]


def parse_line(line: str, idx) -> dict:
    lower = line.lower()

    stat_type, stat_start = None, None
    for pattern, name in STAT_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            stat_type, stat_start = name, m.start()
            break

    cutoff = stat_start if stat_start is not None else len(line)
    player_name = line[:cutoff].strip()
    remainder = lower[cutoff:]

    dir_match = re.search(DIRECTION_PATTERN, remainder)
    direction = None
    if dir_match:
        direction = "over" if dir_match.group(1) in ("over", "o") else "under"

    line_match = re.search(LINE_VALUE_PATTERN, remainder)
    line_value = float(line_match.group(1)) if line_match else None

    prop_id = f"{idx}-{_slugify(player_name)}-{stat_type or 'unknown'}"

    return {
        "id": prop_id,
        "raw_text": line,
        "player_name": player_name,
        "stat_type": stat_type,
        "direction": direction,  # None means "evaluate both sides"
        "line_value": line_value,
        "parse_ok": bool(player_name and stat_type and line_value is not None),
    }


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(parse_props(text), indent=2))
