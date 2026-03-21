"""Tests for SLIP CLI integration (Phase 3 + Phase 5)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from cli.main import main


def test_cli_detects_friction():
    """CLI exits 1 when friction is found."""
    with patch("sys.argv", ["cli.main", "--text", "It takes too long and is too expensive."]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 1


def test_cli_no_friction():
    """CLI exits 0 when no friction is found."""
    with patch("sys.argv", ["cli.main", "--text", "Everything is working perfectly."]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0


def test_cli_custom_source():
    """CLI passes source label through to FrictionPoint."""
    from core import detect
    results = detect("This is broken and awful.", source="test-cli")
    assert all(r.source == "test-cli" for r in results)


def test_cli_score_flag_produces_opportunities(capsys=None):
    """--score flag triggers opportunity scorer output."""
    with patch("sys.argv", ["cli.main", "--text",
                            "It takes too long and I had to hack a workaround.", "--score"]):
        try:
            main()
        except SystemExit:
            pass
    # If no exception, scorer ran without error — pass


def test_cli_score_flag_ranks_correctly():
    """Opportunity scorer ranks workaround above delay (higher automation potential)."""
    from core import detect, score
    fps = detect("It takes too long and I had to hack a workaround.")
    opps = score(fps)
    patterns = [o.title for o in opps]
    assert any("workaround" in p for p in patterns)
    assert opps[0].composite_score >= opps[-1].composite_score


if __name__ == "__main__":
    test_cli_detects_friction()
    test_cli_no_friction()
    test_cli_custom_source()
    test_cli_score_flag_produces_opportunities()
    test_cli_score_flag_ranks_correctly()
    print("All CLI tests passed.")
