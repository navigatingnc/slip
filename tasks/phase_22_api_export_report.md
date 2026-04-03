# phase_22_api_export_report

Goal: Add a `GET /reports/{report_id}/export` endpoint to the local API that streams a CSV of the ranked opportunities for a given persisted SlipReport, completing export parity between the CLI (`--export`, phase 10) and the REST API.

Inputs:
* Existing API in `api/app.py` (phases 8, 12, 15, 17, 21).
* `load_report_by_id()` from `core/persistence.py` (phase 15).
* CSV row format already defined in `core/export.py` (phase 10).

Outputs:
* `api/app.py` gains `GET /reports/{report_id}/export`; it loads the report by ID, builds a CSV in-memory, and returns it as a `text/csv` streaming response with a `Content-Disposition` attachment header. Returns 404 if the report ID is not found.
* `api/test_app.py` gains tests: export returns 200 with `text/csv` content type; CSV contains the expected header row; returns 404 for an unknown report ID.

Constraints:
* Atomic improvement: export endpoint only, no changes to existing endpoints.
* No breaking changes to phases 2–21.
* Follows README dev model: ≤400 tokens of code + description.
