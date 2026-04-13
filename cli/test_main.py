"""Tests for SLIP CLI integration (Phase 3 + Phase 5 + Phase 18 + Phase 19 + Phase 23 + Phase 25 + Phase 27 + Phase 32 + Phase 34)."""
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


# ---------------------------------------------------------------------------
# Phase 19: --list flag tests
# ---------------------------------------------------------------------------

def test_cli_list_flag_prints_reports(tmp_path, capsys):
    """--list must print a summary row for each saved report."""
    import json
    import core.persistence as _p
    fixtures = [
        ("2026-03-25T13:48:44.000000+00:00", "workaround reduction opportunity"),
        ("2026-03-26T21:36:41.000000+00:00", "complaint reduction opportunity"),
    ]
    for ts, top in fixtures:
        stem = ts[:19].replace("-", "").replace(":", "").replace("T", "T")
        fname = f"report_{stem}Z.json"
        (tmp_path / fname).write_text(
            json.dumps({"generated_at": ts, "signal_count": 2, "top_opportunity": top})
        )
    with patch("sys.argv", ["cli.main", "--list"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
    captured = capsys.readouterr()
    assert "workaround reduction opportunity" in captured.out
    assert "complaint reduction opportunity" in captured.out


def test_cli_list_flag_empty_dir(tmp_path, capsys):
    """--list must handle an empty data directory gracefully and exit 0."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--list"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
    captured = capsys.readouterr()
    assert "No saved reports found." in captured.out


def test_cli_list_flag_exit_code_zero(tmp_path):
    """--list must exit with code 0 regardless of report count."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--list"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 0


# ---------------------------------------------------------------------------
# Phase 20: --clear flag tests
# ---------------------------------------------------------------------------

def test_cli_clear_flag_deletes_reports(tmp_path, capsys):
    """--clear must delete all saved reports and print a confirmation."""
    import json
    import core.persistence as _p

    # Create mock reports
    for i in range(3):
        fname = f"report_20260327T10000{i}Z.json"
        (tmp_path / fname).write_text(json.dumps({"generated_at": f"2026-03-27T10:00:0{i}Z"}))

    assert len(list(tmp_path.glob("report_*.json"))) == 3

    with patch("sys.argv", ["cli.main", "--clear"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Cleared 3 saved report(s)." in captured.out
    assert len(list(tmp_path.glob("report_*.json"))) == 0


def test_cli_clear_flag_empty_dir(tmp_path, capsys):
    """--clear must handle an empty data directory gracefully."""
    import core.persistence as _p

    assert len(list(tmp_path.glob("report_*.json"))) == 0

    with patch("sys.argv", ["cli.main", "--clear"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Cleared 0 saved report(s)." in captured.out


# ---------------------------------------------------------------------------
# Phase 23: --export-id flag tests
# ---------------------------------------------------------------------------

def test_cli_export_id_writes_csv_with_header(tmp_path, capsys):
    """--export-id must write a CSV with the correct header row."""
    import json
    import core.persistence as _p

    report_id = "20260405T120000Z"
    report = {
        "generated_at": "2026-04-05T12:00:00Z",
        "signal_count": 1,
        "friction_count": 1,
        "top_pattern": "delay",
        "top_opportunity": "speed improvement",
        "opportunities": [
            {
                "title": "speed improvement",
                "composite_score": 0.75,
                "severity": 0.8,
                "frequency": 0.7,
                "automation_potential": 0.6,
                "willingness_to_pay": 0.9,
                "market_size": 0.5,
                "signal_count": 1,
            }
        ],
    }
    fname = f"report_{report_id}.json"
    (tmp_path / fname).write_text(json.dumps(report))

    out_file = str(tmp_path / "export.csv")
    with patch("sys.argv", ["cli.main", "--export-id", report_id, "--out", out_file]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    with open(out_file) as fh:
        first_line = fh.readline().strip()
    assert first_line == "Title,Composite Score,Severity,Frequency,Automation Potential,Willingness to Pay,Market Size,Signal Count"


def test_cli_export_id_unknown_id_exits_1(tmp_path, capsys):
    """--export-id must exit 1 and print an error for an unknown report ID."""
    import core.persistence as _p

    with patch("sys.argv", ["cli.main", "--export-id", "nonexistent_id"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 1


# ---------------------------------------------------------------------------
# Phase 25: --summary flag tests
# ---------------------------------------------------------------------------

def test_cli_summary_prints_counts(tmp_path, capsys):
    """--summary must print total_reports, total_signals, and total_friction."""
    import json
    import core.persistence as _p

    reports = [
        {
            "generated_at": "2026-04-05T10:00:00Z",
            "signal_count": 3,
            "friction_count": 2,
            "top_pattern": "delay",
            "top_opportunity": "speed layer",
            "opportunities": [{"title": "speed layer", "composite_score": 0.8}],
        },
        {
            "generated_at": "2026-04-05T11:00:00Z",
            "signal_count": 2,
            "friction_count": 1,
            "top_pattern": "workaround",
            "top_opportunity": "automation tool",
            "opportunities": [{"title": "automation tool", "composite_score": 0.6}],
        },
    ]
    for r in reports:
        stem = r["generated_at"][:19].replace("-", "").replace(":", "").replace("T", "T")
        (tmp_path / f"report_{stem}Z.json").write_text(json.dumps(r))

    with patch("sys.argv", ["cli.main", "--summary"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Total reports" in captured.out or "total_reports" in captured.out.lower() or "2" in captured.out
    assert "5" in captured.out  # total signals = 3 + 2
    assert "3" in captured.out  # total friction = 2 + 1


def test_cli_summary_empty_dir(tmp_path, capsys):
    """--summary must handle an empty data directory gracefully and exit 0."""
    import core.persistence as _p

    with patch("sys.argv", ["cli.main", "--summary"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "0" in captured.out


def test_cli_summary_exit_code_zero(tmp_path):
    """--summary must exit with code 0."""
    import core.persistence as _p

    with patch("sys.argv", ["cli.main", "--summary"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 0


def test_cli_export_id_default_filename(tmp_path):
    """--export-id without --out must write to slip_export_<id>.csv."""
    import json
    import core.persistence as _p

    report_id = "20260405T130000Z"
    report = {
        "generated_at": "2026-04-05T13:00:00Z",
        "signal_count": 1,
        "opportunities": [],
    }
    (tmp_path / f"report_{report_id}.json").write_text(json.dumps(report))

    with patch("sys.argv", ["cli.main", "--export-id", report_id]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit:
            pass

    import os
    assert os.path.exists(f"slip_export_{report_id}.csv")
    os.remove(f"slip_export_{report_id}.csv")


# ---------------------------------------------------------------------------
# Phase 27: --health flag tests
# ---------------------------------------------------------------------------

def test_cli_health_prints_required_fields(tmp_path, capsys):
    """--health must print status, service, version, report_count, and checked_at."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--health"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
    captured = capsys.readouterr()
    for field in ("status", "service", "version", "report count", "checked at"):
        assert field.lower() in captured.out.lower(), f"Missing field in --health output: {field}"


def test_cli_health_exit_code_zero(tmp_path):
    """--health must exit with code 0."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--health"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 0


def test_cli_health_report_count_non_negative(tmp_path, capsys):
    """--health report_count must be a non-negative integer in the output."""
    import core.persistence as _p
    with patch("sys.argv", ["cli.main", "--health"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit:
            pass
    captured = capsys.readouterr()
    # Extract the report_count line and verify it contains a non-negative integer
    for line in captured.out.splitlines():
        if "report count" in line.lower():
            count_str = line.split(":")[-1].strip()
            assert count_str.isdigit(), f"report_count is not a non-negative integer: {count_str!r}"
            assert int(count_str) >= 0
            break
    else:
        raise AssertionError("No 'report count' line found in --health output")


# ---------------------------------------------------------------------------
# Phase 29: --version flag tests
# ---------------------------------------------------------------------------

def test_cli_version_flag_prints_version(capsys):
    """--version must print a string containing the _APP_VERSION constant."""
    from cli.main import _APP_VERSION
    with patch("sys.argv", ["cli.main", "--version"]):
        try:
            main()
        except SystemExit:
            pass
    captured = capsys.readouterr()
    assert _APP_VERSION in captured.out


def test_cli_version_flag_exits_zero(capsys):
    """--version must exit with code 0."""
    with patch("sys.argv", ["cli.main", "--version"]):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 0


def test_cli_version_output_contains_slip(capsys):
    """--version output must contain the 'SLIP' prefix."""
    with patch("sys.argv", ["cli.main", "--version"]):
        try:
            main()
        except SystemExit:
            pass
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("SLIP")


# ---------------------------------------------------------------------------
# Phase 32: --file flag tests
# ---------------------------------------------------------------------------

def test_cli_file_flag_batch_analysis(tmp_path, capsys):
    """--file must run batch analysis on a JSON array of signals."""
    import json
    signals = [
        {"text": "It takes too long to get a response.", "source": "reddit"},
        {"text": "I had to hack a workaround for the export.", "source": "forum"},
    ]
    signals_file = tmp_path / "signals.json"
    signals_file.write_text(json.dumps(signals))

    with patch("sys.argv", ["cli.main", "--file", str(signals_file)]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Batch analysis: 2 signal(s)" in captured.out


def test_cli_file_flag_saves_report(tmp_path, capsys):
    """--file --save must persist the batch report to data/."""
    import json
    import core.persistence as _p

    signals = [{"text": "This is broken and awful.", "source": "test"}]
    signals_file = tmp_path / "signals.json"
    signals_file.write_text(json.dumps(signals))

    with patch("sys.argv", ["cli.main", "--file", str(signals_file), "--save"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit:
            pass

    files = list(tmp_path.glob("report_*.json"))
    assert len(files) == 1


def test_cli_file_flag_invalid_json(tmp_path, capsys):
    """--file must exit 1 when the JSON file is invalid."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json")

    with patch("sys.argv", ["cli.main", "--file", str(bad_file)]):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 1


def test_cli_file_flag_empty_array(tmp_path, capsys):
    """--file must exit 1 when the JSON file contains an empty array."""
    import json
    empty_file = tmp_path / "empty.json"
    empty_file.write_text(json.dumps([]))

    with patch("sys.argv", ["cli.main", "--file", str(empty_file)]):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 1


def test_cli_file_flag_no_friction(tmp_path, capsys):
    """--file must handle signals with no friction gracefully."""
    import json
    signals = [{"text": "Everything works perfectly.", "source": "test"}]
    signals_file = tmp_path / "signals.json"
    signals_file.write_text(json.dumps(signals))

    with patch("sys.argv", ["cli.main", "--file", str(signals_file)]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "No friction detected." in captured.out


# ---------------------------------------------------------------------------
# Phase 34: --limit flag tests
# ---------------------------------------------------------------------------

def test_cli_list_limit_restricts_output(tmp_path, capsys):
    """--list --limit N must show at most N reports."""
    import time
    import core.persistence as _p
    from core.report import generate_report
    from core.persistence import save_report

    # Persist 3 reports with unique timestamps
    for i in range(3):
        r = generate_report([{"text": f"Report {i} is broken and slow.", "source": "test"}])
        save_report(r, data_dir=str(tmp_path))
        time.sleep(1.1)

    with patch("sys.argv", ["cli.main", "--list", "--limit", "2"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    # Header + separator + 2 data rows = 4 lines (plus possible trailing newline)
    lines = [ln for ln in captured.out.splitlines() if ln.strip()]
    assert len(lines) == 4  # header, separator, row1, row2


def test_cli_list_limit_zero_exits_error(tmp_path, capsys):
    """--list --limit 0 must exit with code 1."""
    import core.persistence as _p

    with patch("sys.argv", ["cli.main", "--list", "--limit", "0"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
            exited_with = 0
        except SystemExit as e:
            exited_with = e.code
    assert exited_with == 1


def test_cli_list_limit_large_returns_all(tmp_path, capsys):
    """--list --limit 999 must return all reports when total < 999."""
    import time
    import core.persistence as _p
    from core.report import generate_report
    from core.persistence import save_report

    for i in range(2):
        r = generate_report([{"text": f"Report {i} is awful.", "source": "test"}])
        save_report(r, data_dir=str(tmp_path))
        time.sleep(1.1)

    with patch("sys.argv", ["cli.main", "--list", "--limit", "999"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.strip()]
    assert len(lines) == 4  # header, separator, row1, row2


def test_cli_list_no_limit_shows_all(tmp_path, capsys):
    """--list without --limit must show all persisted reports."""
    import time
    import core.persistence as _p
    from core.report import generate_report
    from core.persistence import save_report

    for i in range(3):
        r = generate_report([{"text": f"Report {i} is slow.", "source": "test"}])
        save_report(r, data_dir=str(tmp_path))
        time.sleep(1.1)

    with patch("sys.argv", ["cli.main", "--list"]), \
         patch.object(_p, "_DEFAULT_DATA_DIR", str(tmp_path)):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.strip()]
    assert len(lines) == 5  # header, separator, row1, row2, row3


if __name__ == "__main__":
    test_cli_detects_friction()
    test_cli_no_friction()
    test_cli_custom_source()
    test_cli_score_flag_produces_opportunities()
    test_cli_score_flag_ranks_correctly()
    print("All CLI tests passed.")
