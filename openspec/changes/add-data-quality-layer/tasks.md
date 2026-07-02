# Tasks: Add Data Quality Layer

## 1. Core Models

- [ ] Add `vnstock/core/quality/models.py`
- [ ] Implement `QualityIssue`
- [ ] Implement `ValidationReport`
- [ ] Add serialization helpers: `to_dict()`, `to_json()`
- [ ] Add tests for report validity and severity aggregation

## 2. Exceptions

- [ ] Add `vnstock/core/quality/exceptions.py`
- [ ] Implement `VnstockQualityError`
- [ ] Implement `DataQualityError`
- [ ] Implement `SchemaValidationError`
- [ ] Implement `FreshnessError`
- [ ] Add tests for strict mode exception behavior

## 3. Configuration

- [ ] Add `QualityConfig` to `vnstock/core/settings.py`
- [ ] Add environment variable parsing
- [ ] Add defaults:
  - `enabled=False`
  - `mode="warn"`
  - `attach_report=True`
- [ ] Add tests for config defaults and env overrides

## 4. Schema Rules

- [ ] Add `vnstock/core/quality/rules/schema.py`
- [ ] Implement required column validation
- [ ] Implement dtype validation
- [ ] Implement empty DataFrame validation
- [ ] Implement all-null column validation

## 5. Numeric Rules

- [ ] Add `vnstock/core/quality/rules/numeric.py`
- [ ] Implement negative price checks
- [ ] Implement negative volume checks
- [ ] Implement null/NaN/inf checks
- [ ] Implement suspicious price scale check

## 6. Temporal Rules

- [ ] Add `vnstock/core/quality/rules/temporal.py`
- [ ] Implement datetime parse validation
- [ ] Implement duplicate time detection
- [ ] Implement monotonic time validation
- [ ] Implement future time detection
- [ ] Add optional missing session validation

## 7. Freshness Rules

- [ ] Add `vnstock/core/quality/rules/freshness.py`
- [ ] Implement stale price board check
- [ ] Implement stale intraday check
- [ ] Implement stale daily OHLCV check
- [ ] Implement missing latest timestamp warning

## 8. OHLCV Validator

- [ ] Add `vnstock/core/quality/validators/ohlcv.py`
- [ ] Validate required schema: `time`, `open`, `high`, `low`, `close`, `volume`
- [ ] Validate OHLC consistency
- [ ] Validate positive prices
- [ ] Validate non-negative volume
- [ ] Validate duplicate timestamps
- [ ] Validate freshness metadata
- [ ] Add unit tests

## 9. Price Board Validator

- [ ] Add `vnstock/core/quality/validators/price_board.py`
- [ ] Validate required minimum schema
- [ ] Validate duplicate symbols
- [ ] Validate floor/reference/ceiling consistency
- [ ] Validate bid/ask consistency
- [ ] Validate non-negative volume fields
- [ ] Validate freshness metadata
- [ ] Add unit tests

## 10. Intraday Trade Validator

- [ ] Add `vnstock/core/quality/validators/intraday.py`
- [ ] Validate required schema: `time`, `price`, `volume`, `match_type`, `id`
- [ ] Validate match type enum
- [ ] Validate duplicate trade IDs
- [ ] Validate positive prices
- [ ] Validate non-negative volumes
- [ ] Add optional market session validation
- [ ] Add unit tests

## 11. Validator Registry

- [ ] Add `vnstock/core/quality/registry.py`
- [ ] Register validators by dataset type
- [ ] Implement `validate_dataframe(...)`
- [ ] Add tests for unsupported dataset type behavior

## 12. UI/API Integration

- [ ] Add `validate` and `quality_mode` kwargs handling in `BaseUI._dispatch`
- [ ] Ensure quality kwargs do not leak into provider method calls
- [ ] Attach `df.attrs["quality"]` when validation runs
- [ ] Raise `DataQualityError` in strict mode
- [ ] Add tests for `warn`, `strict`, and `off` modes

## 13. Provider Contract Tests

- [ ] Add OHLCV sample contract tests for DNSE
- [ ] Add OHLCV sample contract tests for KBS
- [ ] Add OHLCV sample contract tests for VCI
- [ ] Add price board sample contract tests
- [ ] Add intraday sample contract tests

## 14. Documentation

- [ ] Add docs page: `docs/DATA_QUALITY.md`
- [ ] Document validation modes
- [ ] Document issue codes
- [ ] Document example usage
- [ ] Document limitations
- [ ] Add migration note for downstream scanner users
