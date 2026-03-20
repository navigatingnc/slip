# phase_04_opportunity_scorer

Goal:
  Convert a list of FrictionPoints into ranked Opportunity objects using a composite score weighted by frequency, severity, and automation potential.

Inputs:
  - List of `FrictionPoint` objects produced by `core.detect()`

Outputs:
  - List of `Opportunity` objects sorted by `composite_score` descending
  - Each Opportunity includes: title, friction_points, frequency, severity, automation_potential, composite_score

Constraints:
  - Atomic improvement: scoring logic only, no I/O or external calls
  - No breaking changes to Phase 2 detector or Phase 3 CLI
  - Follows README dev model: ≤400 tokens of code + description
  - All logic covered by inline tests
