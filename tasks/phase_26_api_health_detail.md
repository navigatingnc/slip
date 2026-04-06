# phase_26_api_health_detail
Goal: Enrich the `GET /health` endpoint to return structured operational metadata — API version, persisted report count, and UTC timestamp — giving operators an at-a-glance readiness check without loading full report payloads.
Inputs:
* Existing `GET /health` in `api/app.py` (phase 8) returning `{"status": "ok", "service": "slip-api"}`.
* `load_reports()` from `core/persistence.py` (phase 11) for report count.
Outputs:
* `api/app.py` `GET /health` now returns a `HealthResponse` Pydantic model with fields: `status` (str), `service` (str), `version` (str), `report_count` (int), `checked_at` (str ISO-8601 UTC).
* `api/test_app.py` gains 3 new tests: health returns all new keys; health `version` matches app version; health `report_count` is a non-negative integer.
Constraints:
* Atomic improvement: health endpoint enrichment only, no changes to other endpoints.
* No breaking changes to phases 2-25 (existing `status` and `service` keys are preserved).
* Follows README dev model: <=400 tokens of code + description.
