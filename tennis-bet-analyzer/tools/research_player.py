"""Stores and loads structured research findings for a prop.

All web research is performed by the agent (Claude) using its own WebSearch
tool, following workflows/research_player.md. This project never calls an
external search API -- that's a deliberate project rule, not a missing
feature. This module just validates and persists the structured findings the
agent hands it after searching.
"""
import json
from pathlib import Path

REQUIRED_FIELDS = ["recent_match_values", "confidence"]


def save_research(prop_id: str, findings: dict, research_dir: Path) -> Path:
    research_dir = Path(research_dir)
    research_dir.mkdir(parents=True, exist_ok=True)

    findings = {
        "surface": "Unknown",
        "tournament": "Unknown",
        "recent_form_summary": "",
        "stat_trend_summary": "",
        "opponent": None,
        "opponent_factor_summary": "",
        "surface_probability": 0.5,
        "opponent_probability": 0.5,
        "momentum_probability": 0.5,
        "injury_news": "None found",
        "inconclusive": False,
        "notes": "",
        **findings,
    }

    if not findings.get("inconclusive"):
        missing = [f for f in REQUIRED_FIELDS if findings.get(f) is None]
        if missing:
            raise ValueError(
                f"Missing required research fields for {prop_id}: {missing}. "
                f"Set \"inconclusive\": true if research is genuinely inconclusive."
            )

    path = research_dir / f"{prop_id}.json"
    path.write_text(json.dumps(findings, indent=2))
    return path


def load_research(prop_id: str, research_dir: Path) -> dict:
    path = Path(research_dir) / f"{prop_id}.json"
    if not path.exists():
        return {"inconclusive": True, "notes": "No research saved for this prop."}
    return json.loads(path.read_text())
