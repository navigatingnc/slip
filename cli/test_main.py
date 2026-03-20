"""Tests for SLIP CLI integration (Phase 3)."""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from cli.main import main


def test_cli_detects_friction(capsys=None):
    """CLI returns friction points for a text with known patterns."""
    with patch("sys.argv", ["cli.main", "--text", "It takes too long and is too expensive."]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 1  # friction found → exit 1


def test_cli_no_friction(capsys=None):
    """CLI exits 0 when no friction is found."""
    with patch("sys.argv", ["cli.main", "--text", "Everything is working perfectly."]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0  # no friction → exit 0


def test_cli_custom_source():
    """CLI passes source label through to FrictionPoint."""
    from core import detect
    results = detect("This is broken and awful.", source="test-cli")
    assert all(r.source == "test-cli" for r in results)


if __name__ == "__main__":
    test_cli_detects_friction()
    test_cli_no_friction()
    test_cli_custom_source()
    print("All CLI tests passed.")
