# phase_20_cli_clear_reports

Goal: Add a `--clear` flag to the CLI that deletes all persisted SlipReports from the `data/` directory, allowing users to easily reset their local history.

Inputs:
* Existing CLI in `cli/main.py` (phase 19).
* Data directory path logic from `core/persistence.py`.

Outputs:
* `core/persistence.py` gains a `clear_reports()` function that deletes all `.json` files in the data directory.
* `cli/main.py` gains a `--clear` flag; when set, it bypasses analysis, calls `clear_reports()`, and prints a confirmation message.
* `cli/test_main.py` gains tests: `--clear` successfully empties the data directory and exits with code 0.

Constraints:
* Atomic improvement: `clear_reports()` function and `--clear` flag only.
* No breaking changes to phases 2–19.
* Follows README dev model: ≤400 tokens of code + description.
