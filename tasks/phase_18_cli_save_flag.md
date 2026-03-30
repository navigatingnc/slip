# phase_18_cli_save_flag
Goal:
  Add a --save flag to the CLI that persists the full SlipReport to data/
  after analysis, and fix the latent sys.exit(1) bug that causes the CLI to
  return a non-zero exit code on successful runs.

Inputs:
  - Existing CLI in cli/main.py (phases 3 + 5).
  - generate_report() from core/report.py (phase 7).
  - save_report() from core/persistence.py (phase 11).

Outputs:
  - cli/main.py gains --save flag; when set, calls generate_report() +
    save_report() and prints the saved filepath.
  - sys.exit(1) on success replaced with sys.exit(0).
  - cli/test_main.py gains tests: --save writes a file, filepath printed,
    no file written without --save, exit code 0 on success.

Constraints:
  - Atomic improvement: --save flag + exit-code fix only.
  - No breaking changes to phases 2–17.
  - Follows README dev model: ≤400 tokens of code + description.
