# phase_24_api_summary
Goal: Add a `GET /reports/summary` endpoint to the local API that returns aggregate statistics across all persisted SlipReports without loading full report payloads.
Inputs:
* Existing API in `api/app.py` (phases 8, 12, 15, 17, 21, 22).
* `load_reports()` from `core/persistence.py` (phase 11).
Outputs:
* `api/app.py` gains `GET /reports/summary`; it loads all persisted reports, aggregates total_reports, total_signals, total_friction, top_patterns (top-3 most frequent), and top_opportunities (top-3 by composite score across all reports), and returns a JSON summary object.
* `api/test_app.py` gains 4 new tests: summary returns 200; summary has required keys; summary counts are correct; summary returns zeros for an empty data directory.
Constraints:
* Atomic improvement: summary endpoint only, no changes to existing endpoints.
* No breaking changes to phases 2-23.
* Follows README dev model: <=400 tokens of code + description.
