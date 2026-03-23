# phase_08_local_api
Goal:
  Implement a minimal local FastAPI application in `/api/app.py` that exposes a
  single `POST /analyze` endpoint. The endpoint accepts a list of raw signal dicts,
  runs the full `generate_report()` pipeline, and returns the `SlipReport` as JSON —
  making the SLIP engine accessible over HTTP for the first time.
Inputs:
  - JSON body: `{"signals": [{"text": "...", "source": "..."}]}`
Outputs:
  - JSON response matching `SlipReport.to_dict()` schema
  - HTTP 200 on success; HTTP 422 on invalid input (FastAPI default validation)
Constraints:
  - Atomic improvement: API wiring only, no new detection, scoring, or report logic
  - No breaking changes to phases 2–7
  - Follows README dev model: ≤400 tokens of code + description
  - All logic covered by inline tests in `/api/test_app.py` using FastAPI TestClient
