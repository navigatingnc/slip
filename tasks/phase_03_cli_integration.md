# phase_03_cli_integration

Goal:
  Wire the core `detect()` engine into the CLI so users can analyze text for friction from the command line.

Inputs:
  - Text string passed via stdin or `--text` argument
  - Optional `--source` label (default: "cli")

Outputs:
  - Printed list of detected `FrictionPoint` objects (pattern, score, tags)
  - Exit code 0 if no friction found, 1 if friction detected

Constraints:
  - Atomic improvement: CLI wiring only, no new detection logic
  - ≤400 tokens of code + description
  - No breaking changes to Phase 2 core engine
  - All logic covered by inline tests
