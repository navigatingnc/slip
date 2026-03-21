# phase_05_cli_opportunity_output

Goal:
  Wire the Phase 4 opportunity scorer into the CLI via a --score flag, completing the detect → score → report pipeline end-to-end.

Inputs:
  - Text string via --text or stdin
  - Optional --source label (default: cli)
  - Optional --score flag to activate opportunity ranking

Outputs:
  - Friction points (always printed when detected)
  - Ranked Opportunity list (printed only when --score is passed)
  - Exit code 0 if no friction, 1 if friction detected

Constraints:
  - Atomic improvement: CLI wiring only, no new scoring or detection logic
  - No breaking changes to Phase 2 detector, Phase 3 CLI, or Phase 4 scorer
  - Follows README dev model: ≤400 tokens of code + description
  - All logic covered by inline tests
