# phase_13_full_opportunity_scoring
Goal:
  Complete the five-dimension Opportunity Scoring model described in the README
  by adding willingness_to_pay and market_size to the Opportunity dataclass and
  the scorer, so all five planned dimensions (Frequency, Severity, Willingness
  to Pay, Market Size, Automation Potential) contribute to the composite score.
Inputs:
  - Existing FrictionPoint list from detect() / ingest().
  - Pattern-keyed lookup tables for willingness_to_pay and market_size (0.0–1.0).
Outputs:
  - Opportunity objects now carry willingness_to_pay and market_size fields.
  - composite_score is recalculated across all five dimensions with equal weights.
  - SlipReport.to_dict() and the CSV exporter surface the two new fields.
Constraints:
  - Atomic improvement: model + scorer update only, no changes to detection or
    persistence logic.
  - No breaking changes to phases 2–12 (existing callers receive richer objects).
  - Follows README dev model: ≤400 tokens of code + description.
  - All logic covered by updated tests in core/test_scorer.py and core/test_export.py.
