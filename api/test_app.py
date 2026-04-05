"""Tests for SLIP local API (Phase 8 + Phase 12 + Phase 21 + Phase 22)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health_returns_200():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_payload():
    resp = client.get("/health")
    data = resp.json()
    assert data["status"] == "ok"
    assert "slip" in data["service"]


# ---------------------------------------------------------------------------
# /analyze — happy path
# ---------------------------------------------------------------------------

_FRICTION_SIGNALS = [
    {"text": "It takes too long to get a quote.", "source": "reddit"},
    {"text": "I had to hack a workaround for the billing system.", "source": "forum"},
    {"text": "Too expensive and nobody offers a cheaper option.", "source": "review"},
]

_CLEAN_SIGNALS = [
    {"text": "Everything is working great.", "source": "survey"},
]


def test_analyze_returns_200():
    resp = client.post("/analyze", json={"signals": _FRICTION_SIGNALS})
    assert resp.status_code == 200


def test_analyze_response_keys():
    resp = client.post("/analyze", json={"signals": _FRICTION_SIGNALS})
    data = resp.json()
    expected = {
        "generated_at", "signal_count", "friction_count",
        "top_pattern", "top_opportunity", "opportunities",
    }
    assert expected == set(data.keys())


def test_analyze_signal_count_matches_input():
    resp = client.post("/analyze", json={"signals": _FRICTION_SIGNALS})
    assert resp.json()["signal_count"] == len(_FRICTION_SIGNALS)


def test_analyze_friction_detected():
    resp = client.post("/analyze", json={"signals": _FRICTION_SIGNALS})
    assert resp.json()["friction_count"] > 0


def test_analyze_opportunities_sorted_descending():
    resp = client.post("/analyze", json={"signals": _FRICTION_SIGNALS})
    scores = [o["composite_score"] for o in resp.json()["opportunities"]]
    assert scores == sorted(scores, reverse=True)


def test_analyze_top_opportunity_present():
    resp = client.post("/analyze", json={"signals": _FRICTION_SIGNALS})
    data = resp.json()
    assert data["top_opportunity"] is not None
    assert data["top_pattern"] is not None


def test_analyze_opportunity_fields():
    resp = client.post("/analyze", json={"signals": _FRICTION_SIGNALS})
    for opp in resp.json()["opportunities"]:
        assert "title" in opp
        assert "composite_score" in opp
        assert "signal_count" in opp


def test_analyze_clean_signals_zero_friction():
    resp = client.post("/analyze", json={"signals": _CLEAN_SIGNALS})
    data = resp.json()
    assert data["friction_count"] == 0
    assert data["top_pattern"] is None
    assert data["top_opportunity"] is None
    assert data["opportunities"] == []


def test_analyze_single_signal():
    resp = client.post("/analyze", json={"signals": [
        {"text": "This is broken and awful.", "source": "test"}
    ]})
    assert resp.status_code == 200
    assert resp.json()["signal_count"] == 1


def test_analyze_source_label_passthrough():
    resp = client.post("/analyze", json={"signals": [
        {"text": "It takes too long.", "source": "custom-source"}
    ]})
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# /analyze — validation errors
# ---------------------------------------------------------------------------

def test_analyze_empty_signals_list_rejected():
    resp = client.post("/analyze", json={"signals": []})
    assert resp.status_code == 422


def test_analyze_missing_text_field_rejected():
    resp = client.post("/analyze", json={"signals": [{"source": "test"}]})
    assert resp.status_code == 422


def test_analyze_missing_body_rejected():
    resp = client.post("/analyze")
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# /reports
# ---------------------------------------------------------------------------

def test_reports_returns_200():
    resp = client.get("/reports")
    assert resp.status_code == 200


def test_reports_response_keys():
    resp = client.get("/reports")
    data = resp.json()
    assert "count" in data
    assert "reports" in data


def test_reports_count_matches_list_length():
    resp = client.get("/reports")
    data = resp.json()
    assert data["count"] == len(data["reports"])


def test_reports_after_analyze_increases_count(tmp_path, monkeypatch):
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    before = client.get("/reports").json()["count"]
    client.post("/analyze", json={"signals": [
        {"text": "It takes too long and is too expensive.", "source": "test"}
    ]})
    after = client.get("/reports").json()["count"]
    assert after == before + 1


def test_reports_each_entry_has_required_keys():
    # Ensure at least one report exists
    client.post("/analyze", json={"signals": [
        {"text": "Broken and awful workaround.", "source": "test"}
    ]})
    data = client.get("/reports").json()
    for report in data["reports"]:
        assert "generated_at" in report
        assert "signal_count" in report
        assert "opportunities" in report


# ---------------------------------------------------------------------------
# /reports/{report_id}
# ---------------------------------------------------------------------------

def test_report_by_id_returns_200(tmp_path, monkeypatch):
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    # Create a report and extract its ID from the filename
    resp = client.post("/analyze", json={"signals": [
        {"text": "It takes too long to get a quote.", "source": "test"}
    ]})
    assert resp.status_code == 200
    # The saved filename stem is the report_id
    files = list(tmp_path.glob("report_*.json"))
    assert len(files) == 1
    report_id = files[0].stem.replace("report_", "")
    resp2 = client.get(f"/reports/{report_id}")
    assert resp2.status_code == 200


def test_report_by_id_returns_correct_content(tmp_path, monkeypatch):
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [
        {"text": "Broken workaround and too expensive.", "source": "test"}
    ]})
    files = list(tmp_path.glob("report_*.json"))
    report_id = files[0].stem.replace("report_", "")
    data = client.get(f"/reports/{report_id}").json()
    assert "generated_at" in data
    assert "signal_count" in data
    assert "opportunities" in data


def test_report_by_id_returns_404_for_missing():
    resp = client.get("/reports/99991231T999999Z")
    assert resp.status_code == 404


def test_report_by_id_404_detail_message():
    resp = client.get("/reports/00000000T000000Z")
    assert "not found" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /reports/{report_id}
# ---------------------------------------------------------------------------

def test_delete_report_returns_204(tmp_path, monkeypatch):
    """DELETE /reports/{id} must return 204 No Content on success."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [
        {"text": "It takes too long and nobody replies.", "source": "test"}
    ]})
    files = list(tmp_path.glob("report_*.json"))
    report_id = files[0].stem.replace("report_", "")
    resp = client.delete(f"/reports/{report_id}")
    assert resp.status_code == 204


def test_delete_report_removes_from_list(tmp_path, monkeypatch):
    """After DELETE the report must no longer appear in GET /reports."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [
        {"text": "Workaround is slow and overpriced.", "source": "test"}
    ]})
    files = list(tmp_path.glob("report_*.json"))
    report_id = files[0].stem.replace("report_", "")
    client.delete(f"/reports/{report_id}")
    ids_in_list = [
        r.get("generated_at") for r in client.get("/reports").json()["reports"]
    ]
    assert all(report_id not in (i or "") for i in ids_in_list)


def test_delete_report_returns_404_for_missing():
    """DELETE /reports/{id} must return 404 when the report does not exist."""
    resp = client.delete("/reports/99991231T999999Z")
    assert resp.status_code == 404


def test_delete_report_404_detail_message():
    """404 response from DELETE must include 'not found' in detail."""
    resp = client.delete("/reports/00000000T000000Z")
    assert "not found" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /reports  (phase 21 — bulk clear)
# ---------------------------------------------------------------------------

def test_delete_all_reports_returns_200(tmp_path, monkeypatch):
    """DELETE /reports must return 200 with a 'deleted' count."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    # Seed two reports
    client.post("/analyze", json={"signals": [{"text": "It takes too long.", "source": "test"}]})
    import time; time.sleep(1)
    client.post("/analyze", json={"signals": [{"text": "Broken workaround.", "source": "test"}]})
    resp = client.delete("/reports")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 2


def test_delete_all_reports_empties_list(tmp_path, monkeypatch):
    """After DELETE /reports, GET /reports must return an empty list."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [{"text": "Too expensive workaround.", "source": "test"}]})
    client.delete("/reports")
    data = client.get("/reports").json()
    assert data["count"] == 0
    assert data["reports"] == []


def test_delete_all_reports_empty_dir_returns_zero(tmp_path, monkeypatch):
    """DELETE /reports on an empty data dir must return {'deleted': 0}."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    resp = client.delete("/reports")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 0


# ---------------------------------------------------------------------------
# GET /reports/{report_id}/export  (phase 22 — CSV export)
# ---------------------------------------------------------------------------

def test_export_report_returns_200(tmp_path, monkeypatch):
    """GET /reports/{id}/export must return 200 with text/csv content type."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [{"text": "It takes too long and is overpriced.", "source": "test"}]})
    files = list(tmp_path.glob("report_*.json"))
    report_id = files[0].stem.replace("report_", "")
    resp = client.get(f"/reports/{report_id}/export")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_export_report_contains_header_row(tmp_path, monkeypatch):
    """Exported CSV must contain the expected column header row."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [{"text": "Broken workaround and too expensive.", "source": "test"}]})
    files = list(tmp_path.glob("report_*.json"))
    report_id = files[0].stem.replace("report_", "")
    resp = client.get(f"/reports/{report_id}/export")
    first_line = resp.text.splitlines()[0]
    assert "Title" in first_line
    assert "Composite Score" in first_line


def test_export_report_returns_404_for_missing():
    """GET /reports/{id}/export must return 404 when the report does not exist."""
    resp = client.get("/reports/99991231T999999Z/export")
    assert resp.status_code == 404


def test_export_report_content_disposition(tmp_path, monkeypatch):
    """Exported CSV must have a Content-Disposition attachment header."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [{"text": "Nobody offers a cheaper option.", "source": "test"}]})
    files = list(tmp_path.glob("report_*.json"))
    report_id = files[0].stem.replace("report_", "")
    resp = client.get(f"/reports/{report_id}/export")
    assert "attachment" in resp.headers.get("content-disposition", "")
    assert report_id in resp.headers.get("content-disposition", "")


# ---------------------------------------------------------------------------
# GET /reports/summary  (phase 24 — aggregate statistics)
# ---------------------------------------------------------------------------

def test_summary_returns_200():
    """GET /reports/summary must return 200."""
    resp = client.get("/reports/summary")
    assert resp.status_code == 200


def test_summary_has_required_keys():
    """GET /reports/summary response must contain all required keys."""
    resp = client.get("/reports/summary")
    data = resp.json()
    for key in ("total_reports", "total_signals", "total_friction", "top_patterns", "top_opportunities"):
        assert key in data, f"Missing key: {key}"


def test_summary_counts_reflect_persisted_reports(tmp_path, monkeypatch):
    """Summary counts must match the number of signals and friction in persisted reports."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    client.post("/analyze", json={"signals": [
        {"text": "It takes too long and is overpriced.", "source": "test"},
        {"text": "Nobody offers a workaround for this broken flow.", "source": "test"},
    ]})
    resp = client.get("/reports/summary")
    data = resp.json()
    assert data["total_reports"] >= 1
    assert data["total_signals"] >= 2
    assert data["total_friction"] >= 1


def test_summary_empty_data_dir_returns_zeros(tmp_path, monkeypatch):
    """GET /reports/summary must return zero counts when no reports are persisted."""
    import core.persistence as _p
    monkeypatch.setattr(_p, "_DEFAULT_DATA_DIR", str(tmp_path))
    resp = client.get("/reports/summary")
    data = resp.json()
    assert data["total_reports"] == 0
    assert data["total_signals"] == 0
    assert data["total_friction"] == 0
    assert data["top_patterns"] == []
    assert data["top_opportunities"] == []


if __name__ == "__main__":
    test_health_returns_200()
    test_health_payload()
    test_analyze_returns_200()
    test_analyze_response_keys()
    test_analyze_signal_count_matches_input()
    test_analyze_friction_detected()
    test_analyze_opportunities_sorted_descending()
    test_analyze_top_opportunity_present()
    test_analyze_opportunity_fields()
    test_analyze_clean_signals_zero_friction()
    test_analyze_single_signal()
    test_analyze_source_label_passthrough()
    test_analyze_empty_signals_list_rejected()
    test_analyze_missing_text_field_rejected()
    test_analyze_missing_body_rejected()
    test_reports_returns_200()
    test_reports_response_keys()
    test_reports_count_matches_list_length()
    test_reports_after_analyze_increases_count()
    test_reports_each_entry_has_required_keys()
    print("All API tests passed.")
