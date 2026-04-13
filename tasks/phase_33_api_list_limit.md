# phase_33_api_list_limit
Goal: Add a `limit` query parameter to the `GET /reports` endpoint in the local API, allowing users to restrict the number of returned report summaries for better performance as the local history grows.
Inputs: Existing `GET /reports` endpoint in `api/app.py` (phase 12). `load_reports()` helper in `core/persistence.py`.
Outputs:
- `api/app.py`: update `get_reports()` to accept an optional `limit` parameter (min=1); slice the report list before returning; bump `_APP_VERSION` to `"0.33.0"`
- `api/test_app.py`: 3 new tests covering valid limit application, invalid limit (0) rejection, and large limit handling
- `tasks/phase_33_api_list_limit.md`: this task definition
Constraints: Atomic improvement — API list pagination only, no changes to core analysis logic. No breaking changes to existing endpoints. Follows README dev model: ≤400 tokens.
