# phase_28_api_version_sync
Goal: Introduce a module-level `_APP_VERSION` constant in `api/app.py` and bump it to `"0.28.0"`, keeping the API version string in sync with the CLI (phase 27) and eliminating the hard-coded string inside the `FastAPI()` constructor.
Inputs:
* Existing `api/app.py` with `FastAPI(version="0.26.0")` hard-coded in the constructor (phases 8–27).
* `_APP_VERSION = "0.27.0"` pattern established in `cli/main.py` (phase 27).
Outputs:
* `api/app.py` gains `_APP_VERSION = "0.28.0"` module-level constant; the `FastAPI()` constructor uses `version=_APP_VERSION` instead of a hard-coded string.
* `api/test_app.py` gains 2 new tests: health version field matches `_APP_VERSION`; `_APP_VERSION` follows semantic versioning format `MAJOR.MINOR.PATCH`.
Constraints:
* Atomic improvement: version constant introduction only, no changes to endpoints or schemas.
* No breaking changes to phases 2-27 (health endpoint still returns the correct version string).
* Follows README dev model: <=400 tokens of code + description.
