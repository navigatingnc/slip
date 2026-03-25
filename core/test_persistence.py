"""Tests for the persistence module — Phase 11."""
import os
from .models import FrictionPoint, Opportunity
from .report import SlipReport
from .persistence import save_report, load_reports


def _make_report(top: str = "delay") -> SlipReport:
    fp = FrictionPoint(description="slow process", pattern=top, score=0.75)
    opp = Opportunity(
        title=f"{top} reduction opportunity",
        friction_points=[fp],
        frequency=1.0,
        severity=0.75,
        automation_potential=0.8,
        composite_score=0.78,
    )
    return SlipReport(
        signal_count=1,
        friction_count=1,
        opportunities=[opp],
        top_pattern=top,
        top_opportunity=opp.title,
    )


def test_save_report_creates_file(tmp_path):
    report = _make_report()
    filepath = save_report(report, data_dir=str(tmp_path))
    assert os.path.isfile(filepath)
    assert filepath.endswith(".json")


def test_save_report_content(tmp_path):
    import json

    report = _make_report("cost")
    filepath = save_report(report, data_dir=str(tmp_path))
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["signal_count"] == 1
    assert data["top_pattern"] == "cost"
    assert len(data["opportunities"]) == 1


def test_load_reports_returns_sorted(tmp_path):
    import time

    r1 = _make_report("delay")
    save_report(r1, data_dir=str(tmp_path))
    time.sleep(1)  # ensure distinct timestamps
    r2 = _make_report("gap")
    save_report(r2, data_dir=str(tmp_path))

    loaded = load_reports(data_dir=str(tmp_path))
    assert len(loaded) == 2
    assert loaded[0]["top_pattern"] == "delay"
    assert loaded[1]["top_pattern"] == "gap"


def test_load_reports_empty_dir(tmp_path):
    loaded = load_reports(data_dir=str(tmp_path))
    assert loaded == []
