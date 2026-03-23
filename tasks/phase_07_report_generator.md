# phase_07_report_generator
Goal:
  Implement a report generator in `/core/report.py` that consumes the output of the
  full ingest → detect → score pipeline and produces a structured `SlipReport`
  dataclass, serialisable to a plain dict (JSON-ready). This closes the end-to-end
  batch analysis loop before the API and agent layers are introduced.
Inputs:
  - List of raw signal dicts (same format accepted by `core.ingest()`)
Outputs:
  - `SlipReport` object containing: signal_count, friction_count, opportunities
    (ranked), top_pattern, top_opportunity, and a generated_at timestamp
Constraints:
  - Atomic improvement: report assembly only, no new detection or scoring logic
  - No breaking changes to phases 2–6
  - Follows README dev model: ≤400 tokens of code + description
  - All logic covered by inline tests in `/core/test_report.py`
