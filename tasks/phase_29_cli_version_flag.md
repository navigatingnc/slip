# phase_29_cli_version_flag
Goal: Add a `--version` flag to the CLI that prints the `_APP_VERSION` string and exits 0, and bump `_APP_VERSION` to `"0.29.0"` to keep the CLI in sync with the API cadence.
Inputs:
* Existing CLI in `cli/main.py` with `_APP_VERSION = "0.27.0"` (phase 27).
* `--health` flag already printing version as part of a multi-field table (phase 27).
Outputs:
* `cli/main.py` `_APP_VERSION` bumped to `"0.29.0"`.
* `cli/main.py` gains `--version` flag; when supplied the CLI prints `SLIP <_APP_VERSION>` and exits 0.
* `cli/test_main.py` gains 3 new tests: version flag prints the version string; version flag exits 0; version output contains the semver constant.
Constraints:
* Atomic improvement: --version flag and version bump only, no changes to other flags or endpoints.
* No breaking changes to phases 2-28.
* Follows README dev model: <=400 tokens of code + description.
