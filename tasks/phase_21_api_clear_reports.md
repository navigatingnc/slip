# phase_21_api_clear_reports

Goal: Add a `DELETE /reports` endpoint to the local API that deletes all persisted SlipReports from the `data/` directory, completing full CRUD parity between the CLI and the REST API.

Inputs:
* Existing API in `api/app.py` (phases 8, 12, 15, 17).
* `clear_reports()` from `core/persistence.py` (phase 20).

Outputs:
* `api/app.py` gains a `DELETE /reports` endpoint; it calls `clear_reports()` and returns `{"deleted": N}` with HTTP 200.
* `api/test_app.py` gains tests: `DELETE /reports` removes all reports and returns the correct count; calling it on an empty directory returns `{"deleted": 0}`.

Constraints:
* Atomic improvement: `DELETE /reports` endpoint only.
* No breaking changes to phases 2–20.
* Follows README dev model: ≤400 tokens of code + description.
