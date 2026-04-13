# phase_34_cli_list_limit
Goal: Add a `--limit N` flag to the CLI that restricts the number of reports shown by `--list`, mirroring the `GET /reports?limit=N` parameter added to the API in phase 33.
Inputs: Existing `--list` flag in `cli/main.py` (phase 19) that calls `load_reports()` and displays all reports. Phase 33 API `limit` parameter as the parity target.
Outputs:
- `cli/main.py`: new `--limit N` argument; validation (must be >= 1); slice applied before `_print_report_list()`; bump `_APP_VERSION` to `"0.34.0"`; update docstring
- `cli/test_main.py`: 4 new tests covering limit restriction, invalid limit (0) rejection, large limit, and no-limit baseline
- `tasks/phase_34_cli_list_limit.md`: this task definition
Constraints: Atomic improvement — CLI list limit only, no changes to core logic or API. No breaking changes to phases 1–33. Follows README dev model: ≤400 tokens.
