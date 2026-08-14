"""Regression tests for Phase 36 API offset pagination."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def _seed_reports(data_dir, count):
    for index in range(count):
        report = {
            "generated_at": f"2026-01-01T00:00:0{index}+00:00",
            "signal_count": index + 1,
            "friction_count": 0,
            "opportunities": [],
        }
        (data_dir / f"report_20260101T00000{index}Z.json").write_text(
            json.dumps(report), encoding="utf-8"
        )


def test_reports_offset_skips_oldest_reports(tmp_path, monkeypatch):
    import core.persistence as persistence

    monkeypatch.setattr(persistence, "_DEFAULT_DATA_DIR", str(tmp_path))
    _seed_reports(tmp_path, 4)

    data = client.get("/reports?offset=1").json()
    assert data["count"] == 3
    assert data["total_count"] == 4
    assert data["reports"][0]["signal_count"] == 2


def test_reports_offset_applies_before_limit(tmp_path, monkeypatch):
    import core.persistence as persistence

    monkeypatch.setattr(persistence, "_DEFAULT_DATA_DIR", str(tmp_path))
    _seed_reports(tmp_path, 4)

    data = client.get("/reports?offset=1&limit=2").json()
    assert data["count"] == 2
    assert data["total_count"] == 4
    assert [report["signal_count"] for report in data["reports"]] == [2, 3]


def test_reports_offset_boundary_validation(tmp_path, monkeypatch):
    import core.persistence as persistence

    monkeypatch.setattr(persistence, "_DEFAULT_DATA_DIR", str(tmp_path))
    _seed_reports(tmp_path, 2)

    page = client.get("/reports?offset=99").json()
    assert page == {"count": 0, "total_count": 2, "reports": []}
    assert client.get("/reports?offset=-1").status_code == 422
