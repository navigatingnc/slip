# phase_19_cli_list_reports

Goal: Add a `--list` flag to the CLI that retrieves and prints a summary of all persisted SlipReports from the `data/` directory, providing a local history view.

Inputs:
* Existing CLI in `cli/main.py` (phase 18).
* `load_reports()` from `core/persistence.py` (phase 11).

Outputs:
* `cli/main.py` gains a `--list` flag; when set, it bypasses analysis, calls `load_reports()`, and prints a formatted list of saved reports (showing ID/timestamp, signal count, and top opportunity).
* `cli/test_main.py` gains tests: `--list` prints expected report summaries, handles empty data directory gracefully, and exits with code 0.

Constraints:
* Atomic improvement: `--list` flag and formatting logic only.
* No breaking changes to phases 2–18.
* Follows README dev model: ≤400 tokens of code + description.
