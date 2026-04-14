# phase_35_reports_total_count
Goal: Add a `total_count` field to the `GET /reports` response so callers always know the full unfiltered report count, even when a `limit` is applied (phase 33). Without this, clients cannot determine how many reports exist beyond the current page.
Inputs: `ReportsResponse` model and `get_reports()` in `api/app.py` (phase 33). `load_reports()` in `core/persistence.py`.
Outputs:
- `api/app.py`: add `total_count: int` to `ReportsResponse`; update `get_reports()` to compute total before slicing; bump `_APP_VERSION` to `"0.35.0"`
- `api/test_app.py`: update `test_reports_response_keys` to assert `total_count`; add `total_count` assertions to phase 33 limit tests; add 2 new dedicated phase 35 tests
- `tasks/phase_35_reports_total_count.md`: this task definition
Constraints: Atomic improvement — response schema addition only, no changes to core logic or CLI. No breaking changes to phases 1–34 (additive field). Follows README dev model: ≤400 tokens.
