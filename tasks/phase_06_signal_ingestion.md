# phase_06_signal_ingestion
Goal:
  Implement a signal ingestion module in `/core/ingestion.py` that accepts raw text
  signals from named sources, normalises them into a uniform `Signal` dataclass, and
  feeds them through the existing `detect()` pipeline — bridging external input to the
  detect → score → report chain.
Inputs:
  - List of dicts with keys `text` (str) and `source` (str)
Outputs:
  - List of `FrictionPoint` objects produced by `core.detect()` across all signals
Constraints:
  - Atomic improvement: ingestion normalisation only, no new detection or scoring logic
  - No breaking changes to Phase 2 detector, Phase 4 scorer, or Phase 5 CLI
  - Follows README dev model: ≤400 tokens of code + description
  - All logic covered by inline tests in `/core/test_ingestion.py`
