# phase_02_core_friction_detection

Goal:
  Implement the core friction detection logic in `/core` — the foundational engine that scans text signals for friction patterns and returns scored FrictionPoint objects.

Inputs:
  - Raw text string (signal from any source: forum post, review, workflow description)
  - Optional source label (e.g. "reddit", "review", "manual")

Outputs:
  - List of `FrictionPoint` objects, each with: description, pattern, source, score (0.0–1.0), tags

Constraints:
  - Atomic improvement: core detection only, no I/O or external calls
  - ≤400 tokens of code + description
  - No breaking changes to Phase 1 scaffold
  - All logic covered by inline tests
