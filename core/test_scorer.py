"""Tests for SLIP opportunity scorer (Phase 4)."""
from core.scorer import score
from core.models import FrictionPoint, Opportunity


def _fp(pattern: str, s: float = 0.25) -> FrictionPoint:
    return FrictionPoint(description="test signal", pattern=pattern, score=s)


def test_score_empty():
    assert score([]) == []


def test_score_single_pattern():
    results = score([_fp("delay"), _fp("delay")])
    assert len(results) == 1
    opp = results[0]
    assert opp.title == "delay reduction opportunity"
    assert opp.frequency == 1.0
    assert 0.0 < opp.composite_score <= 1.0


def test_score_multiple_patterns():
    fps = [_fp("delay"), _fp("workaround"), _fp("cost")]
    results = score(fps)
    assert len(results) == 3
    # Sorted descending by composite_score
    scores = [o.composite_score for o in results]
    assert scores == sorted(scores, reverse=True)


def test_score_returns_opportunity_objects():
    results = score([_fp("gap")])
    assert all(isinstance(o, Opportunity) for o in results)


def test_score_automation_potential_applied():
    workaround = score([_fp("workaround")])[0]
    complaint = score([_fp("complaint")])[0]
    # workaround has higher automation potential (0.9 vs 0.4)
    assert workaround.automation_potential > complaint.automation_potential


if __name__ == "__main__":
    test_score_empty()
    test_score_single_pattern()
    test_score_multiple_patterns()
    test_score_returns_opportunity_objects()
    test_score_automation_potential_applied()
    print("All scorer tests passed.")
