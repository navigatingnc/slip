# phase_23_cli_export_by_id
Goal: Add a `--export-id` flag to the CLI that loads a persisted SlipReport by its ID and exports its ranked opportunities to a CSV file, completing CLI/API export parity for saved reports.
Inputs:
* Existing CLI in `cli/main.py` (phases 3, 5, 10, 18, 19, 20).
* `load_report_by_id()` from `core/persistence.py` (phase 15).
* `export_opportunities()` from `core/export.py` (phase 10).
Outputs:
* `cli/main.py` gains `--export-id <REPORT_ID>` and `--out <FILE>` arguments; when `--export-id` is supplied the CLI loads the report by ID, exports its opportunities to the path given by `--out` (default: `slip_export_<id>.csv`), prints a confirmation, and exits 0. Exits 1 with an error message if the report ID is not found.
* `cli/test_main.py` gains tests: export-by-id writes a CSV with the correct header; exits 1 for an unknown ID.
Constraints:
* Atomic improvement: `--export-id` / `--out` flags only, no changes to existing flags.
* No breaking changes to phases 2–22.
* Follows README dev model: ≤400 tokens of code + description.
