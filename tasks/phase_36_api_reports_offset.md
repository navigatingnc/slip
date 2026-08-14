# phase_36_api_reports_offset
Goal: Add an `offset` query parameter to `GET /reports` so callers can page through local report history alongside the existing `limit` and `total_count` fields.
Inputs: `get_reports()` and `ReportsResponse` in `api/app.py` (phases 33 and 35).
Outputs:
- `api/app.py`: add non-negative `offset` (default 0); apply it before `limit`; bump `_APP_VERSION` to `"0.36.0"`
- `api/test_offset_pagination.py`: cover offset, offset-plus-limit, past-end, and invalid-offset behavior
- `tasks/phase_36_api_reports_offset.md`: this task definition
Constraints: Atomic, additive API pagination improvement. No core or CLI changes; existing `limit` behavior remains unchanged.
