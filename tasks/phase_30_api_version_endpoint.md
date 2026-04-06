# phase_30_api_version_endpoint

Goal: Add a dedicated `GET /version` endpoint to the API that returns `{"version": _APP_VERSION, "service": "slip-api"}` and bump `_APP_VERSION` to `"0.30.0"`, mirroring the CLI `--version` flag introduced in phase 29.

Inputs: Existing `api/app.py` with `_APP_VERSION = "0.28.0"` and no dedicated `/version` route (phases 8–28). CLI `--version` flag established in phase 29.

Outputs: `api/app.py` gains a `VersionResponse` schema and `GET /version` endpoint tagged `["meta"]`; `_APP_VERSION` bumped to `"0.30.0"`. `api/test_app.py` gains 3 new tests: endpoint returns 200; payload contains `version` and `service` keys; `version` value matches `_APP_VERSION`.

Constraints: Atomic improvement — version endpoint only, no changes to other routes or schemas. No breaking changes to phases 2–29. Follows README dev model: ≤400 tokens.
