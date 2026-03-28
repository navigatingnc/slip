# phase_15_api_report_by_id
Goal:
  Add a GET /reports/{report_id} endpoint to the local FastAPI that returns
  a single persisted report by its ID (the timestamp stem of the filename,
  e.g. "20260327T002427Z"), completing the CRUD read surface for reports.
Inputs:
  - Existing GET /reports list endpoint (phase 12).
  - Persisted JSON files in data/ named report_{id}.json.
Outputs:
  - GET /reports/{report_id} → 200 with the report dict, or 404 if not found.
  - core/persistence.py gains load_report_by_id(report_id, data_dir) helper.
  - api/test_app.py gains tests: 200 hit, 404 miss, correct content returned.
Constraints:
  - Atomic improvement: one new endpoint + one helper function only.
  - No breaking changes to phases 2–14.
  - Follows README dev model: ≤400 tokens of code + description.
