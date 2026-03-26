# phase_12_api_reports_endpoint
Goal:
  Expose a GET /reports endpoint on the local FastAPI app that returns all
  persisted SlipReport JSON files from the data/ directory, making the
  Phase 11 persistence layer accessible over HTTP for the first time.
Inputs:
  - No request body; reads from the data/ directory via load_reports().
Outputs:
  - JSON response: {"count": N, "reports": [...]} where each element is a
    SlipReport dict as produced by SlipReport.to_dict().
  - HTTP 200 with an empty reports list when no reports have been saved yet.
Constraints:
  - Atomic improvement: API wiring only, no changes to persistence or core logic.
  - No breaking changes to phases 2–11.
  - Follows README dev model: ≤400 tokens of code + description.
  - All logic covered by inline tests in api/test_app.py using FastAPI TestClient.
