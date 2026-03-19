"""Basic tests for the SLIP core friction detector."""

from core.detector import detect
from core.models import FrictionPoint


def test_detect_delay():
    results = detect("It takes too long to get a quote from them.", source="test")
    assert len(results) == 1
    assert results[0].pattern == "delay"
    assert results[0].score > 0


def test_detect_complaint():
    results = detect("This tool is broken and awful.", source="test")
    assert any(r.pattern == "complaint" for r in results)


def test_detect_no_friction():
    results = detect("Everything works perfectly and on time.", source="test")
    assert results == []


def test_detect_multiple_patterns():
    results = detect(
        "It's too expensive and takes too long, I had to hack a workaround.",
        source="test",
    )
    patterns = {r.pattern for r in results}
    assert "delay" in patterns
    assert "cost" in patterns
    assert "workaround" in patterns


def test_friction_point_repr():
    fp = FrictionPoint(description="slow process", pattern="delay", score=0.5)
    assert "delay" in repr(fp)
    assert "0.50" in repr(fp)


if __name__ == "__main__":
    test_detect_delay()
    test_detect_complaint()
    test_detect_no_friction()
    test_detect_multiple_patterns()
    test_friction_point_repr()
    print("All tests passed.")
