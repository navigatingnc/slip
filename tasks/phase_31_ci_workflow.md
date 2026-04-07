# phase_31_ci_workflow

Goal: Fix all pre-existing ruff lint violations across the codebase and add a `ruff.toml` configuration file, establishing a clean lint baseline ready for CI. The GitHub Actions workflow file will be added in a future phase once the `workflow` token scope is available.

Inputs: 12 ruff violations across `agents/`, `api/`, `cli/`, and `core/` (phases 1–30). No `ruff.toml` exists.

Outputs:
- `ruff.toml`: lint config selecting E + F rules, ignoring E501 (line-length) for now
- `agents/slip_agent.py`: remove unused `Optional` and `ingest` imports (F401)
- `api/test_app.py`: split semicolon line into two statements (E702)
- `cli/main.py`: remove f-string placeholders from plain strings (F541)
- `core/export.py`: remove unused `List` import (F401)
- `core/report.py`: remove unused `asdict` import (F401)
- `core/test_export.py`: remove unused `os` import (F401)
- `core/test_persistence.py`: remove unused `load_report_by_id` import (F401)
- `core/test_report.py`: remove unused `Opportunity`, `FrictionPoint` imports (F401)

Constraints: Atomic improvement — lint fixes and config only, no changes to application logic. No breaking changes to phases 2–30. Follows README dev model: ≤400 tokens.
