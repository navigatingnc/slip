"""Tests for SLIP local API (Phase 8)."""
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
    print("All API tests passed.")
