# phase_17_api_delete_report
Goal:
  Add a DELETE /reports/{report_id} endpoint to the local FastAPI that removes
  a single persisted report by its ID, completing the full CRUD read/write
  surface for reports (Create via POST /analyze, Read via GET /reports and
  GET /reports/{id}, Delete via DELETE /reports/{id}).

Inputs:
  - Existing GET /reports/{report_id} endpoint and load_report_by_id() helper
    (phase 15).
  - Persisted JSON files in data/ named report_{id}.json.

Outputs:
  - DELETE /reports/{report_id} → 204 No Content on success, 404 if not found.
  - core/persistence.py gains delete_report(report_id, data_dir) helper.
  - api/test_app.py gains tests: 204 on valid delete, 404 on missing,
    report no longer returned by GET /reports after deletion.

Constraints:
  - Atomic improvement: one new endpoint + one helper function only.
  - No breaking changes to phases 2–16.
  - Follows README dev model: ≤400 tokens of code + description.
