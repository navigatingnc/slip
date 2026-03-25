# phase_11_report_persistence
Goal:
  Implement a JSON persistence layer in `core/persistence.py` that saves and loads
  SlipReport objects to/from the `data/` directory, fulfilling the README's
  local-first, privacy-first design principle. Wire it into SlipAgent so every
  `analyze()` call is automatically persisted to disk.
Inputs:
  - `save_report(report, data_dir)`: Writes a SlipReport as a timestamped JSON file
    under `data/`.
  - `load_reports(data_dir)`: Reads all saved JSON report files and returns a list
    of plain dicts (JSON-ready).
Outputs:
  - A `.json` file per report in `data/`, named by UTC timestamp
    (e.g. `data/report_20260325T120000Z.json`).
  - `load_reports()` returns a list of report dicts sorted oldest-first.
Constraints:
  - Atomic improvement: persistence wiring only, no changes to detection/scoring logic.
  - No breaking changes to phases 2–10.
  - Follows README dev model: ≤400 tokens of code + description.
  - All logic covered by inline tests in `core/test_persistence.py`.
