"""JSON persistence layer for SLIP — Phase 11.

Saves and loads SlipReport objects to/from the local `data/` directory,
fulfilling the README's local-first, privacy-first design principle.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from .report import SlipReport

_DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _data_dir(data_dir: str | None) -> str:
    path = os.path.abspath(data_dir or _DEFAULT_DATA_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def save_report(report: SlipReport, data_dir: str | None = None) -> str:
    """Persist a SlipReport to a timestamped JSON file in *data_dir*.

    Args:
        report:   The SlipReport to save.
        data_dir: Target directory (defaults to ``data/`` at repo root).

    Returns:
        Absolute path of the written file.
    """
    directory = _data_dir(data_dir)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"report_{timestamp}.json"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
    return filepath


def load_reports(data_dir: str | None = None) -> List[Dict[str, Any]]:
    """Load all persisted SlipReport JSON files from *data_dir*.

    Args:
        data_dir: Source directory (defaults to ``data/`` at repo root).

    Returns:
        List of report dicts sorted by ``generated_at`` ascending (oldest first).
    """
    directory = _data_dir(data_dir)
    reports: List[Dict[str, Any]] = []
    for fname in os.listdir(directory):
        if fname.startswith("report_") and fname.endswith(".json"):
            filepath = os.path.join(directory, fname)
            with open(filepath, "r", encoding="utf-8") as f:
                reports.append(json.load(f))
    return sorted(reports, key=lambda r: r.get("generated_at", ""))
