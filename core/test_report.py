"""Tests for SLIP report generator (Phase 7)."""
from core.report import SlipReport, generate_report


# --- generate_report() ---

_SIGNALS = [
    {"text": "It takes too long to get a quote.", "source": "reddit"},
    {"text": "I had to hack a workaround for the billing system.", "source": "forum"},
    {"text": "Too expensive and nobody offers a cheaper option.", "source": "review"},
    {"text": "Everything is working great today.", "source": "survey"},
]


def test_report_returns_slip_report():
    report = generate_report(_SIGNALS)
    assert isinstance(report, SlipReport)


def test_report_signal_count():
    report = generate_report(_SIGNALS)
    assert report.signal_count == len(_SIGNALS)


def test_report_friction_count_positive():
    report = generate_report(_SIGNALS)
    assert report.friction_count > 0


def test_report_friction_count_zero_for_clean_signals():
    clean = [{"text": "Everything works perfectly.", "source": "test"}]
    report = generate_report(clean)
    assert report.friction_count == 0
    assert report.top_pattern is None
    assert report.top_opportunity is None
    assert report.opportunities == []


def test_report_opportunities_sorted_descending():
    report = generate_report(_SIGNALS)
    scores = [o.composite_score for o in report.opportunities]
    assert scores == sorted(scores, reverse=True)


def test_report_top_pattern_is_string():
    report = generate_report(_SIGNALS)
    assert isinstance(report.top_pattern, str)


def test_report_top_opportunity_is_string():
    report = generate_report(_SIGNALS)
    assert isinstance(report.top_opportunity, str)


def test_report_top_opportunity_matches_first_ranked():
    report = generate_report(_SIGNALS)
    if report.opportunities:
        assert report.top_opportunity == report.opportunities[0].title


def test_report_empty_signals():
    report = generate_report([])
    assert report.signal_count == 0
    assert report.friction_count == 0
    assert report.opportunities == []
    assert report.top_pattern is None
    assert report.top_opportunity is None


def test_report_generated_at_is_iso_string():
    report = generate_report(_SIGNALS)
    assert isinstance(report.generated_at, str)
    assert "T" in report.generated_at  # ISO 8601 format


# --- SlipReport.to_dict() ---

def test_to_dict_keys():
    report = generate_report(_SIGNALS)
    d = report.to_dict()
    expected_keys = {
        "generated_at", "signal_count", "friction_count",
        "top_pattern", "top_opportunity", "opportunities",
    }
    assert expected_keys == set(d.keys())


def test_to_dict_opportunities_structure():
    report = generate_report(_SIGNALS)
    d = report.to_dict()
    for opp in d["opportunities"]:
        assert "title" in opp
        assert "composite_score" in opp
        assert "signal_count" in opp


def test_to_dict_is_json_serialisable():
    import json
    report = generate_report(_SIGNALS)
    # Should not raise
    json.dumps(report.to_dict())


# --- SlipReport.__repr__() ---

def test_repr_contains_key_fields():
    report = generate_report(_SIGNALS)
    r = repr(report)
    assert "SlipReport" in r
    assert "signals=" in r
    assert "friction=" in r


if __name__ == "__main__":
    test_report_returns_slip_report()
    test_report_signal_count()
    test_report_friction_count_positive()
    test_report_friction_count_zero_for_clean_signals()
    test_report_opportunities_sorted_descending()
    test_report_top_pattern_is_string()
    test_report_top_opportunity_is_string()
    test_report_top_opportunity_matches_first_ranked()
    test_report_empty_signals()
    test_report_generated_at_is_iso_string()
    test_to_dict_keys()
    test_to_dict_opportunities_structure()
    test_to_dict_is_json_serialisable()
    test_repr_contains_key_fields()
    print("All report tests passed.")
