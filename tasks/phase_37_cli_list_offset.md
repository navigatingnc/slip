# phase_37_cli_list_offset
Goal: Add a `--offset N` flag to the CLI so `--list` can page through local report history alongside the existing `--limit N` flag.
Inputs: `--list` and `--limit` handling in `cli/main.py` (phases 19 and 34). API offset behavior from phase 36 as the parity target.
Outputs:
- `cli/main.py`: add a non-negative `--offset` argument (default 0); apply it before `--limit`; bump `_APP_VERSION` to `"0.37.0"`
- `cli/test_main.py`: cover offset, offset-plus-limit, past-end, and invalid-offset behavior
- `tasks/phase_37_cli_list_offset.md`: this task definition
Constraints: Atomic CLI pagination improvement only. No core or API changes; existing `--limit` behavior remains unchanged.
