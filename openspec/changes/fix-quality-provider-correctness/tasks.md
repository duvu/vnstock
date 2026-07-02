# Tasks: Fix Quality and Provider Correctness Findings

## 1. Global Quality Config

- [ ] Update `BaseUI._dispatch()` to load `get_config().quality` before popping quality kwargs
- [ ] Make `validate` default to `get_config().quality.enabled`
- [ ] Make `quality_mode` default to `get_config().quality.mode`
- [ ] Preserve explicit per-call `validate=False` override
- [ ] Preserve explicit per-call `quality_mode="off"|"warn"|"strict"` override
- [ ] Add unit test: env-enabled validation runs without `validate=True`
- [ ] Add unit test: `validate=False` disables validation even when env-enabled
- [ ] Add unit test: `VNSTOCK_QUALITY_MODE=strict` raises on validation errors

## 2. Index-Safe Row Reporting

- [ ] Replace all `row_index=int(idx)` patterns in quality layer
- [ ] Add helper for positional issue iteration, e.g. `_iter_bad_positions(mask, max_examples)`
- [ ] Store positional row offset in `QualityIssue.row_index`
- [ ] Store original index label in `QualityIssue.context["index_label"]` where useful
- [ ] Update temporal rules:
  - [ ] datetime parse
  - [ ] duplicate time
  - [ ] monotonic time
  - [ ] future time
- [ ] Update numeric rules:
  - [ ] negative price
  - [ ] negative volume
  - [ ] null/NaN/inf
  - [ ] price scale
- [ ] Update OHLCV validator consistency checks
- [ ] Update price board validator checks
- [ ] Update intraday validator checks
- [ ] Add regression test: OHLCV validator with `DatetimeIndex`
- [ ] Add regression test: temporal rules with string index
- [ ] Add regression test: intraday validator with string index
- [ ] Add regression test: price board validator with string index

## 3. Observable Internal Validation Failures

- [ ] Add issue code `QUALITY_VALIDATION_INTERNAL_ERROR`
- [ ] Add helper to create synthetic validation failure report
- [ ] In warn mode, attach synthetic report to `df.attrs["quality"]` when validator raises unexpectedly
- [ ] In warn mode, emit `UserWarning` for internal validation failures
- [ ] In strict mode, re-raise unexpected validation exceptions or wrap them in `DataQualityError`
- [ ] Do not silently `pass` unexpected validation errors
- [ ] Add unit test: warn mode internal validator exception attaches synthetic report
- [ ] Add unit test: strict mode internal validator exception raises

## 4. Freshness Metadata Normalization

- [ ] Add `_coerce_datetime(value)` helper in `freshness.py`
- [ ] Accept `datetime.datetime`
- [ ] Accept `pandas.Timestamp`
- [ ] Accept ISO datetime strings
- [ ] Return `None` for unparseable values instead of crashing
- [ ] Normalize all comparison timestamps to UTC-aware datetimes
- [ ] Add unit test: `df.attrs["fetched_at"]` as ISO string
- [ ] Add unit test: timezone-naive `fetched_at`
- [ ] Add unit test: invalid string `fetched_at` returns missing metadata warning

## 5. Intraday Session Timezone Handling

- [ ] Convert timezone-aware timestamps to `Asia/Ho_Chi_Minh` before session checks
- [ ] Treat timezone-naive timestamps as already local by default
- [ ] Add unit test: UTC timestamp corresponding to 09:15 ICT is inside session
- [ ] Add unit test: UTC timestamp corresponding to 08:00 ICT is outside session
- [ ] Add unit test: timezone-naive 09:15 is inside session

## 6. Provider Model Type Fixes

- [ ] Change `ProviderComparisonReport.issues` from `list[str]` to `list[ProviderIssue]`
- [ ] Ensure `ProviderComparisonReport.to_dict()` serializes issue objects safely
- [ ] Ensure `ProviderComparisonReport.to_json()` serializes issue objects safely
- [ ] Change `score_health()` signature to `capabilities_checked: list[str] | None = None`
- [ ] Pass `capabilities_checked=capabilities_checked or []` into `ProviderHealth`
- [ ] Update health tests for capability key preservation
- [ ] Update comparison report serialization tests

## 7. Provider Invalid Input Guards

- [ ] Add `DRIFT_INVALID_INPUT` guard in `detect_drift()`
- [ ] Guard against `None`
- [ ] Guard against non-DataFrame objects
- [ ] Add `COMPARE_INVALID_INPUT` guard in `compare_ohlcv()`
- [ ] Guard against non-dict input
- [ ] Guard against dict values that are not DataFrames
- [ ] Guard against missing required OHLCV columns before `.copy()`, `pd.to_datetime`, and `.set_index()`
- [ ] Add unit test: `detect_drift(None, ...)`
- [ ] Add unit test: `detect_drift({})`
- [ ] Add unit test: `compare_ohlcv(None, ...)`
- [ ] Add unit test: `compare_ohlcv({"DNSE": None}, ...)`
- [ ] Add unit test: `compare_ohlcv()` with missing `time` column

## 8. Provider Contract Tests Must Fail on Interface Drift

- [ ] Remove broad `try/except Exception: pytest.skip(...)` blocks from contract tests
- [ ] Ensure adapter imports fail the test if module path changes
- [ ] Ensure method signature changes fail the test
- [ ] Add explicit skip only for intentionally optional live tests, not offline contract tests
- [ ] Add grep/regression check or test asserting no `pytest.skip` in `tests/contracts/providers/` for adapter failures

## 9. Documentation Updates

- [ ] Update `docs/DATA_QUALITY.md` to explain global env behavior
- [ ] Document `QUALITY_VALIDATION_INTERNAL_ERROR`
- [ ] Document `row_index` as positional offset, not index label
- [ ] Document original label in `context["index_label"]`
- [ ] Update `docs/PROVIDER_HARDENING.md` for structured `ProviderIssue` comparison reports
- [ ] Document invalid input issue codes:
  - `DRIFT_INVALID_INPUT`
  - `COMPARE_INVALID_INPUT`
  - `COMPARE_MISSING_COLUMN` if implemented

## 10. Verification

- [ ] Run `ruff check .`
- [ ] Run `ruff format --check .`
- [ ] Run `PYTHONPATH=. pytest -m "not slow" tests/unit/core tests/unit/ui tests/unified_ui tests/contracts`
- [ ] Run `PYTHONPATH=. pytest tests/unit/core/quality tests/unit/core/provider tests/contracts/providers -q`
- [ ] Run `python -m build --sdist --wheel --no-isolation`
- [ ] Confirm CI passes on Python 3.10, 3.11, 3.12, 3.13
- [ ] Confirm no unresolved high-priority review findings remain
