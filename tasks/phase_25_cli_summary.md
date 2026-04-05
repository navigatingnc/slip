# phase_25_cli_summary
Goal: Add a `--summary` flag to the CLI that prints aggregate statistics across all persisted SlipReports, mirroring the API's GET /reports/summary for quick terminal access.
Inputs:
* Existing CLI in `cli/main.py` (phases 3, 5, 18, 19, 20, 23).
* `load_reports()` from `core/persistence.py` (phase 11).
Outputs:
* `cli/main.py` gains `--summary` flag; when supplied the CLI loads all persisted reports, computes total_reports, total_signals, total_friction, top-3 patterns, and top-3 opportunities, prints a formatted summary table, and exits 0.
* `cli/test_main.py` gains 3 new tests: summary prints correct counts; summary handles empty data directory; summary exits 0.
Constraints:
* Atomic improvement: --summary flag only, no changes to existing flags.
* No breaking changes to phases 2-24.
* Follows README dev model: <=400 tokens of code + description.
