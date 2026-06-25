"""Logs prop predictions and their eventual real-world outcomes, so
estimate_probability.py's calibration can be checked over a real sample size
instead of judged off any single slate.

results_log.json lives at the project root, not in .tmp/ -- it's the one
piece of local state in this project meant to persist across sessions rather
than be regenerated.
"""
import json
import re
from datetime import date
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "results_log.json"


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "unknown"


def _load(log_path: Path = LOG_PATH) -> list:
    if not log_path.exists():
        return []
    return json.loads(log_path.read_text())


def _save(entries: list, log_path: Path = LOG_PATH) -> None:
    log_path.write_text(json.dumps(entries, indent=2))


def log_new_evaluations(evaluations: list, log_path: Path = LOG_PATH) -> int:
    """Appends a pending entry for every evaluated prop that got a real
    probability (unparseable / insufficient-data props are skipped -- there's
    nothing to calibrate there). Returns the number of entries added."""
    entries = _load(log_path)
    existing_ids = {e["log_id"] for e in entries}
    today = date.today().isoformat()
    added = 0

    for e in evaluations:
        if e.get("true_probability") is None:
            continue
        log_id = f"{today}-{_slugify(e['player_name'])}-{e['stat_type']}-{e['line_value']}"
        if log_id in existing_ids:
            continue
        entries.append({
            "log_id": log_id,
            "date_logged": today,
            "player_name": e["player_name"],
            "stat_type": e["stat_type"],
            "direction": e["direction"],
            "line_value": e["line_value"],
            "raw_text": e["raw_text"],
            "true_probability": e["true_probability"],
            "rating": e["rating"],
            "edge_pct": e.get("edge_pct"),
            "status": "pending",
            "actual_value": None,
            "hit": None,
            "date_resolved": None,
        })
        added += 1

    _save(entries, log_path)
    return added


def pending_entries(log_path: Path = LOG_PATH) -> list:
    return [e for e in _load(log_path) if e["status"] == "pending"]


def resolve_entry(log_id: str, actual_value: float, log_path: Path = LOG_PATH) -> dict:
    entries = _load(log_path)
    for e in entries:
        if e["log_id"] == log_id:
            e["actual_value"] = actual_value
            e["hit"] = actual_value > e["line_value"] if e["direction"] == "over" else actual_value < e["line_value"]
            e["status"] = "resolved"
            e["date_resolved"] = date.today().isoformat()
            _save(entries, log_path)
            return e
    raise KeyError(f"No logged entry with log_id {log_id}")


def void_entry(log_id: str, reason: str = "", log_path: Path = LOG_PATH) -> dict:
    entries = _load(log_path)
    for e in entries:
        if e["log_id"] == log_id:
            e["status"] = "void"
            e["date_resolved"] = date.today().isoformat()
            e["void_reason"] = reason
            _save(entries, log_path)
            return e
    raise KeyError(f"No logged entry with log_id {log_id}")


def calibration_report(log_path: Path = LOG_PATH) -> dict:
    entries = [e for e in _load(log_path) if e["status"] == "resolved"]

    by_rating = {}
    for e in entries:
        bucket = by_rating.setdefault(e["rating"], {"n": 0, "hits": 0, "prob_sum": 0.0})
        bucket["n"] += 1
        bucket["hits"] += 1 if e["hit"] else 0
        bucket["prob_sum"] += e["true_probability"]

    summary = {
        rating: {
            "n": b["n"],
            "hit_rate": round(b["hits"] / b["n"], 4) if b["n"] else None,
            "avg_predicted_probability": round(b["prob_sum"] / b["n"], 4) if b["n"] else None,
        }
        for rating, b in by_rating.items()
    }

    overall_n = len(entries)
    overall_hits = sum(1 for e in entries if e["hit"])
    return {
        "by_rating": summary,
        "overall": {
            "n": overall_n,
            "hit_rate": round(overall_hits / overall_n, 4) if overall_n else None,
        },
    }
