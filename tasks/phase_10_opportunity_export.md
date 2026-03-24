# phase_10_opportunity_export
Goal:
  Implement a CSV exporter in `/core/export.py` to allow users to export the ranked Opportunities from a `SlipReport` to a CSV file for external analysis, and wire it into the CLI via a `--export` flag.
Inputs:
  - `export_opportunities(report, filepath)`: Takes a `SlipReport` object and a target file path.
Outputs:
  - A CSV file containing columns: Title, Composite Score, Severity, Frequency, Automation Potential, Signal Count.
  - CLI prints a success message when export is complete.
Constraints:
  - Atomic improvement: Export wiring only, no changes to core detection/scoring logic.
  - No breaking changes to phases 2–9.
  - Follows README dev model: ≤400 tokens of code + description.
  - All logic covered by inline tests in `/core/test_export.py`.
