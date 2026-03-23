"""Tests for SLIP signal ingestion module (Phase 6)."""
from core.ingestion import Signal, normalise, ingest
from core.models import FrictionPoint


# --- Signal dataclass ---

def test_signal_strips_whitespace():
    s = Signal(text="  slow process  ", source="test")
    assert s.text == "slow process"


def test_signal_default_source():
    s = Signal(text="some text")
    assert s.source == "unknown"


def test_signal_repr_contains_source():
    s = Signal(text="broken tool", source="reddit")
    assert "reddit" in repr(s)


def test_signal_rejects_non_string_text():
    try:
        Signal(text=123)  # type: ignore[arg-type]
        assert False, "Expected TypeError"
    except TypeError:
        pass


# --- normalise() ---

def test_normalise_basic():
    sig = normalise({"text": "It takes too long", "source": "forum"})
    assert sig.text == "It takes too long"
    assert sig.source == "forum"


def test_normalise_missing_source_defaults():
    sig = normalise({"text": "broken"})
    assert sig.source == "unknown"


def test_normalise_extra_keys_go_to_metadata():
    sig = normalise({"text": "slow", "source": "yelp", "rating": 1})
    assert sig.metadata == {"rating": 1}


def test_normalise_empty_text():
    sig = normalise({"text": ""})
    assert sig.text == ""


# --- ingest() ---

def test_ingest_returns_friction_points():
    signals = [
        {"text": "It takes too long to get a quote.", "source": "reddit"},
        {"text": "I had to hack a workaround for this.", "source": "forum"},
    ]
    results = ingest(signals)
    assert len(results) > 0
    assert all(isinstance(fp, FrictionPoint) for fp in results)


def test_ingest_preserves_source_labels():
    signals = [{"text": "too expensive and slow", "source": "yelp"}]
    results = ingest(signals)
    assert all(fp.source == "yelp" for fp in results)


def test_ingest_skips_empty_text():
    signals = [{"text": "", "source": "empty"}, {"text": "   ", "source": "blank"}]
    results = ingest(signals)
    assert results == []


def test_ingest_empty_list():
    assert ingest([]) == []


def test_ingest_multiple_sources_independent():
    signals = [
        {"text": "It takes too long.", "source": "source_a"},
        {"text": "Everything is perfect.", "source": "source_b"},
    ]
    results = ingest(signals)
    sources = {fp.source for fp in results}
    assert "source_a" in sources
    assert "source_b" not in sources  # no friction in second signal


if __name__ == "__main__":
    test_signal_strips_whitespace()
    test_signal_default_source()
    test_signal_repr_contains_source()
    test_signal_rejects_non_string_text()
    test_normalise_basic()
    test_normalise_missing_source_defaults()
    test_normalise_extra_keys_go_to_metadata()
    test_normalise_empty_text()
    test_ingest_returns_friction_points()
    test_ingest_preserves_source_labels()
    test_ingest_skips_empty_text()
    test_ingest_empty_list()
    test_ingest_multiple_sources_independent()
    print("All ingestion tests passed.")
