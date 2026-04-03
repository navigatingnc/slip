"""Tests for the persistence module — Phase 11 + Phase 17."""
import os
from .models import FrictionPoint, Opportunity
from .report import SlipReport
from .persistence import clear_reports, delete_report, load_report_by_id, load_reports, save_report


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


# ---------------------------------------------------------------------------
# Phase 17: delete_report tests
# ---------------------------------------------------------------------------

def test_delete_report_removes_file(tmp_path):
    """delete_report must remove the JSON file and return True."""
    report = _make_report()
    filepath = save_report(report, data_dir=str(tmp_path))
    report_id = os.path.basename(filepath).replace("report_", "").replace(".json", "")
    result = delete_report(report_id, data_dir=str(tmp_path))
    assert result is True
    assert not os.path.isfile(filepath)


def test_delete_report_returns_false_for_missing(tmp_path):
    """delete_report must return False when the report ID does not exist."""
    result = delete_report("99991231T999999Z", data_dir=str(tmp_path))
    assert result is False


def test_delete_report_not_in_load_reports_after_deletion(tmp_path):
    """Deleted report must no longer appear in load_reports."""
    report = _make_report("gap")
    filepath = save_report(report, data_dir=str(tmp_path))
    report_id = os.path.basename(filepath).replace("report_", "").replace(".json", "")
    delete_report(report_id, data_dir=str(tmp_path))
    loaded = load_reports(data_dir=str(tmp_path))
    assert all(r.get("top_pattern") != "gap" for r in loaded)


# ---------------------------------------------------------------------------
# Phase 20: clear_reports tests
# ---------------------------------------------------------------------------

def test_clear_reports_removes_all_files(tmp_path):
    """clear_reports must remove all JSON files and return the count."""
    import time
    r1 = _make_report("delay")
    save_report(r1, data_dir=str(tmp_path))
    time.sleep(1)  # ensure distinct timestamps
    r2 = _make_report("gap")
    save_report(r2, data_dir=str(tmp_path))
    
    # Add a non-report file
    (tmp_path / "not_a_report.txt").write_text("ignore me")
    
    count = clear_reports(data_dir=str(tmp_path))
    assert count == 2
    
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].name == "not_a_report.txt"
