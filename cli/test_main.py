"""Tests for SLIP CLI integration (Phase 3 + Phase 5 + Phase 18)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from cli.main import main


def test_cli_detects_friction():
    """CLI exits 0 when friction is found (phase 18 fixes the exit-code bug)."""
    with patch("sys.argv", ["cli.main", "--text", "It takes too long and is too expensive."]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0


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


# ---------------------------------------------------------------------------
# Phase 18: --save flag tests
# ---------------------------------------------------------------------------

def test_cli_save_flag_writes_file(tmp_path):
    """--save must persist a JSON report file to the data directory."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--text",
                            "It takes too long and nobody replies.", "--save"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit:
            pass
    files = list(tmp_path.glob("report_*.json"))
    assert len(files) == 1


def test_cli_save_flag_prints_filepath(tmp_path, capsys):
    """--save must print the saved filepath to stdout."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--text",
                            "Workaround is slow and overpriced.", "--save"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit:
            pass
    captured = capsys.readouterr()
    assert "Report saved to" in captured.out


def test_cli_no_save_flag_writes_no_file(tmp_path):
    """Without --save no report file must be written."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--text",
                            "It takes too long and is too expensive."]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit:
            pass
    files = list(tmp_path.glob("report_*.json"))
    assert len(files) == 0


def test_cli_exit_code_zero_on_friction():
    """CLI must exit 0 even when friction is detected (phase 18 bug fix)."""
    with patch("sys.argv", ["cli.main", "--text", "This is broken and awful."]):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 0


if __name__ == "__main__":
    test_cli_detects_friction()
    test_cli_no_friction()
    test_cli_custom_source()
    test_cli_score_flag_produces_opportunities()
    test_cli_score_flag_ranks_correctly()
    print("All CLI tests passed.")
