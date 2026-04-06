# phase_27_cli_health_check
Goal: Add a `--health` flag to the CLI that prints operational metadata — app version, persisted report count, and UTC timestamp — mirroring the API's enriched `GET /health` response for quick terminal readiness checks.
Inputs:
* Existing CLI in `cli/main.py` (phases 3, 5, 18, 19, 20, 23, 25).
* `load_reports()` from `core/persistence.py` (phase 11).
* App version constant defined in `cli/main.py`.
Outputs:
* `cli/main.py` gains `--health` flag; when supplied the CLI prints a formatted health table with fields: `status` (ok), `service` (slip-cli), `version`, `report_count`, and `checked_at` (ISO-8601 UTC), then exits 0.
* `cli/main.py` gains a `_APP_VERSION` module-level constant (`"0.27.0"`) used by both the health output and the `--version` flag (if present).
* `cli/test_main.py` gains 3 new tests: health prints all required fields; health exits 0; health report_count is a non-negative integer.
Constraints:
* Atomic improvement: --health flag only, no changes to existing flags.
* No breaking changes to phases 2-26.
* Follows README dev model: <=400 tokens of code + description.
