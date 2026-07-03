# Task Completion
- Preferred full verification is `make verify`.
- For focused code changes, run the smallest relevant pytest command with `PYTHONPATH=.` plus `make lint` or `make format`/`make lint` as appropriate.
- `pytest.ini` is the active pytest config: strict markers/config, verbose output by default, 300s timeout.
- Tests do not auto-register package-level user keys. Integration tests may call external services; configure provider-specific credentials directly when needed.
- If only Markdown docs changed and pre-commit is unavailable, at minimum run `git diff --check -- <file>` and report that full pre-commit could not be run.