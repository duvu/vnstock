# Data Quality Layer

`vnstock` includes a built-in data quality layer that validates returned `DataFrame` objects before they reach downstream code. Validation is **opt-in** by default and does not change existing behaviour unless explicitly enabled.

---

## Validation Modes

| Mode | Behaviour |
|---|---|
| `off` | No validation. Default when `validate` kwarg is absent and `VNSTOCK_QUALITY_ENABLED=false` (the default). |
| `warn` | Run validation, attach `ValidationReport` to `df.attrs["quality"]`, emit a `UserWarning` when errors are found. Does not raise. |
| `strict` | Run validation, raise `DataQualityError` if the report contains at least one error. |

Enable globally via environment variable:

```bash
export VNSTOCK_QUALITY_ENABLED=true
export VNSTOCK_QUALITY_MODE=warn   # or strict
```

Or enable per-call:

```python
df = Market().equity("FPT").ohlcv(
    start="2025-01-01",
    end="2026-07-02",
    source="DNSE",
    validate=True,
    quality_mode="warn",   # default when validate=True
)
```

---

## Using the Validation Report

When `validate=True` and `quality_mode` is `"warn"` or `"strict"`, the `ValidationReport` is attached to `df.attrs["quality"]`:

```python
report = df.attrs["quality"]

print(report.valid)           # True / False
print(report.severity)        # "info" | "warning" | "error"
print(report.row_count)       # number of rows validated

for issue in report.errors:
    print(issue.code, issue.message, issue.column, issue.row_index)

for issue in report.warnings:
    print(issue.code, issue.message)
```

Serialize for logging:

```python
import json
print(json.dumps(report.to_dict(), indent=2))
```

---

## Direct Validation API

Validate any `DataFrame` directly without going through the UI layer:

```python
from vnstock.core.quality import validate_dataframe

report = validate_dataframe(
    df,
    dataset_type="ohlcv",   # "ohlcv" | "price_board" | "intraday_trades"
    provider="DNSE",
    symbol="FPT",
    interval="1D",
)
```

---

## Issue Codes

### Schema

| Code | Severity | Description |
|---|---|---|
| `SCHEMA_MISSING_COLUMN` | error | A required column is absent. |
| `SCHEMA_EMPTY_DATAFRAME` | error | DataFrame has zero rows. |
| `SCHEMA_INVALID_DTYPE` | warning | Column has unexpected dtype kind. |
| `SCHEMA_COLUMN_ALL_NULL` | warning | Column is entirely null/NaN. |

### Numeric

| Code | Severity | Description |
|---|---|---|
| `NUMERIC_NEGATIVE_PRICE` | error | Price column has a negative value. |
| `NUMERIC_NEGATIVE_VOLUME` | error | Volume column has a negative value. |
| `NUMERIC_NULL_VALUE` | warning | Numeric column has null/NaN. |
| `NUMERIC_INF_VALUE` | error | Numeric column has infinite value. |
| `OHLC_PRICE_SCALE_SUSPICIOUS` | warning | Price value outside plausible range (100–200,000,000 VND). |

### OHLC Consistency

| Code | Severity | Description |
|---|---|---|
| `OHLC_HIGH_BELOW_LOW` | error | `high < low`. |
| `OHLC_HIGH_BELOW_OPEN` | error | `high < open`. |
| `OHLC_HIGH_BELOW_CLOSE` | error | `high < close`. |
| `OHLC_LOW_ABOVE_OPEN` | error | `low > open`. |
| `OHLC_LOW_ABOVE_CLOSE` | error | `low > close`. |

### Temporal

| Code | Severity | Description |
|---|---|---|
| `TIME_MISSING` | warning | Null timestamp in time column. |
| `TIME_INVALID` | error | Timestamp could not be parsed. |
| `TIME_DUPLICATED` | warning | Duplicate timestamp in time column. |
| `TIME_NOT_MONOTONIC` | warning | Time column is not monotonically increasing. |
| `TIME_FUTURE_VALUE` | warning | Timestamp is in the future. |
| `TIME_MISSING_SESSIONS` | info | Expected trading session date is absent. |

### Price Board

| Code | Severity | Description |
|---|---|---|
| `BOARD_DUPLICATE_SYMBOL` | warning | Same ticker appears more than once. |
| `BOARD_PRICE_OUTSIDE_FLOOR_CEILING` | error | `close_price` or `reference_price` is outside `[floor, ceiling]`. |
| `BOARD_MISSING_REFERENCE_PRICE` | warning | `reference_price` is outside the price band. |
| `BOARD_BID_ASK_CROSSED` | warning | Best bid price exceeds best ask price. |
| `BOARD_NEGATIVE_BID_VOLUME` | error | Bid volume is negative. |
| `BOARD_NEGATIVE_ASK_VOLUME` | error | Ask volume is negative. |

### Intraday Trades

| Code | Severity | Description |
|---|---|---|
| `TRADE_INVALID_MATCH_TYPE` | error | `match_type` is not one of `buy`, `sell`, `unknown`, `ato`, `atc`. |
| `TRADE_DUPLICATE_ID` | warning | Duplicate `id` value. |
| `TRADE_SYNTHETIC_ID` | info | Trade `id` was synthesized (not provided by the exchange). |
| `TRADE_NON_POSITIVE_PRICE` | error | Trade price is zero or negative. |
| `TRADE_NEGATIVE_VOLUME` | error | Trade volume is negative. |
| `TRADE_TIME_OUTSIDE_SESSION` | warning | Trade time falls outside the configured market session window. |

### Freshness

| Code | Severity | Description |
|---|---|---|
| `FRESHNESS_STALE` | warning | Data age exceeds the configured staleness threshold. |
| `FRESHNESS_LATEST_TIME_MISSING` | warning | No parseable timestamp found to evaluate freshness. |
| `FRESHNESS_FETCHED_AT_MISSING` | warning | No `fetched_at` metadata and no row timestamps. |

---

## Configuration

All configuration lives in `QualityConfig` (part of `vnstock.core.settings`):

| Setting | Default | Env var |
|---|---|---|
| `enabled` | `False` | `VNSTOCK_QUALITY_ENABLED` |
| `mode` | `"warn"` | `VNSTOCK_QUALITY_MODE` |
| `attach_report` | `True` | `VNSTOCK_QUALITY_ATTACH_REPORT` |
| `max_error_examples` | `20` | — |
| `stale_price_board_seconds` | `30` | `VNSTOCK_QUALITY_STALE_PRICE_BOARD_SECONDS` |
| `stale_intraday_seconds` | `60` | `VNSTOCK_QUALITY_STALE_INTRADAY_SECONDS` |
| `stale_daily_ohlcv_hours` | `36` | `VNSTOCK_QUALITY_STALE_DAILY_OHLCV_HOURS` |
| `check_missing_sessions` | `True` | `VNSTOCK_QUALITY_CHECK_MISSING_SESSIONS` |
| `check_session_time` | `False` | `VNSTOCK_QUALITY_CHECK_SESSION_TIME` |

---

## Strict Mode Example

```python
from vnstock.core.quality.exceptions import DataQualityError

try:
    df = Market().equity("FPT").ohlcv(
        start="2025-01-01",
        end="2026-07-02",
        source="DNSE",
        validate=True,
        quality_mode="strict",
    )
except DataQualityError as e:
    print("Validation failed:", e.report.severity)
    for err in e.report.errors:
        print(f"  [{err.code}] {err.message}")
```

---

## Supported Dataset Types

| `dataset_type` | Description |
|---|---|
| `ohlcv` | OHLCV bar data (daily, weekly, intraday bars) |
| `price_board` | Live price board snapshots |
| `intraday_trades` | Individual trade ticks |

Types `reference` and `fundamental` are planned but not yet implemented.

---

## Limitations

- Validation is provider-agnostic. It cannot detect provider-specific encoding bugs (e.g. price already divided by 1000 by one provider but not another).
- The freshness check depends on either `df.attrs["fetched_at"]` or the latest row timestamp. Providers that do not populate this field will trigger `FRESHNESS_FETCHED_AT_MISSING`. `fetched_at` is normalised via `_coerce_datetime()` and accepts `datetime`, `pd.Timestamp`, and ISO 8601 strings.
- Missing trading session detection (`TIME_MISSING_SESSIONS`) requires the caller to supply `expected_dates`. The default CI does not supply a trading calendar.
- Session time validation (`TRADE_TIME_OUTSIDE_SESSION`, `check_session_time`) is disabled by default because pre-open and post-close data is legitimate in some use cases. When enabled, tz-aware timestamps are converted to `Asia/Ho_Chi_Minh`; tz-naive timestamps are treated as local Vietnam time.
- The data quality layer does not repair or modify data values.
- When validation fails due to an internal Python error (e.g. a bug in a rule), a `RuntimeWarning` with code `QUALITY_VALIDATION_INTERNAL_ERROR` is emitted in `warn`/`strict` mode. Data is returned unmodified in all cases. Use `quality_mode="off"` to suppress this warning.
- `row_index` in `QualityIssue` is always the 0-based positional row offset regardless of the DataFrame's actual index type (integer, DatetimeIndex, string, etc.).

---

## Migration Note for Downstream Scanner Users

If you previously implemented custom `DataFrame` validation in a scanner or backtesting pipeline, you can replace that logic with `validate_dataframe`:

```python
# Before
def check_my_ohlcv(df):
    if "close" not in df.columns:
        raise ValueError("missing close")
    if (df["high"] < df["low"]).any():
        raise ValueError("OHLC inconsistency")

# After
from vnstock.core.quality import validate_dataframe

report = validate_dataframe(df, dataset_type="ohlcv", provider="DNSE", symbol=ticker)
if not report.valid:
    for err in report.errors:
        print(f"[{err.code}] {err.message}")
```

The `validate_dataframe` function returns a `ValidationReport`; it does not raise by default. Pass the report to your own error handling logic, or use `quality_mode="strict"` to let vnstock raise `DataQualityError` automatically.
