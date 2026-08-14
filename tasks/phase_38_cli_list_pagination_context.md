# phase_38_cli_list_pagination_context
Goal: Make CLI report-list pagination self-describing after phases 34 and 37 added `--limit` and `--offset`.
Inputs: `cli/main.py` report-list output and the existing local report collection.
Outputs:
- `cli/main.py`: show selected count, total saved reports, and offset after non-empty `--list` output; clarify a past-end empty page; bump `_APP_VERSION` to `"0.38.0"`.
- `cli/test_main.py`: cover pagination summary, past-end context, and revised list line counts.
- `tasks/phase_38_cli_list_pagination_context.md`: this task definition.
Constraints: Atomic CLI-only UX improvement. Preserve slicing, validation, and empty-history behavior.
