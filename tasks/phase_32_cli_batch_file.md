# phase_32_cli_batch_file
Goal: Add a `--file` flag to the CLI that reads a JSON array of signal objects from a file and runs the full batch analysis pipeline, bridging the gap between single-text CLI input and the planned multi-source Opportunity Discovery Engine.
Inputs: Existing `generate_report()` pipeline (phase 7) that already handles multi-signal batches. CLI `main.py` with single-text `--text` input only.
Outputs:
- `cli/main.py`: new `--file JSON_FILE` argument; batch analysis branch that calls `generate_report()` directly; supports `--save` and `--export` flags; error handling for invalid/empty JSON; bump `_APP_VERSION` to `"0.32.0"`
- `cli/test_main.py`: 5 new tests covering batch analysis, save, invalid JSON, empty array, and no-friction edge cases
- `tasks/phase_32_cli_batch_file.md`: this task definition
Constraints: Atomic improvement — CLI batch input only, no changes to core logic. No breaking changes to phases 1–31. Follows README dev model: ≤400 tokens.
