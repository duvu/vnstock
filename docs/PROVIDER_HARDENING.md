# Provider Hardening

This document describes the provider hardening layer added in `vnstock/core/provider/`. It covers capability registry, schema drift detection, cross-provider comparison, health scoring, the router integration tests, and the capability matrix.

---

## Overview

The provider hardening layer adds deterministic, offline-verifiable guarantees around the data pipeline:

| Component | Module | Purpose |
|-----------|--------|---------|
| Capability registry | `vnstock/core/provider/capabilities.py` | Declares what each provider supports |
| Schema drift detection | `vnstock/core/provider/drift.py` | Detects when adapter output deviates from baseline schema |
| Cross-provider comparison | `vnstock/core/provider/compare.py` | Compares OHLCV DataFrames from multiple providers |
| Health scoring | `vnstock/core/provider/health.py` | Derives a health snapshot from collected issues |
| Capability matrix | `vnstock/core/provider/matrix.py` | Builds and renders a provider × capability support table |
| Provider models | `vnstock/core/provider/models.py` | `ProviderCapability`, `ProviderIssue`, `ProviderHealth`, `ProviderComparisonReport` |

---

## Capability Registry

`CAPABILITIES` is a list of `ProviderCapability` frozen dataclasses, one per (provider, dataset_type, asset_class) combination.

```python
from vnstock.core.provider.capabilities import query_capabilities

# All VCI OHLCV capabilities
caps = query_capabilities(provider="VCI", dataset_type="ohlcv")

# All equity capabilities across providers
equity_caps = query_capabilities(asset_class="equity")
```

Registered providers: **KBS**, **VCI**, **DNSE**, **MSN**, **FMP**, **FMARKET**.

---

## Schema Drift Detection

Use `detect_drift()` to compare a normalized DataFrame against the stored baseline schema for a provider.

```python
from vnstock.core.provider.drift import detect_drift

issues = detect_drift(df, provider="vci", dataset_type="ohlcv")
for issue in issues:
    print(f"[{issue.severity}] {issue.code}: {issue.message}")
```

Issue codes:

| Code | Severity | Meaning |
|------|----------|---------|
| `DRIFT_MISSING_COLUMN` | error | Required column absent from DataFrame |
| `DRIFT_DTYPE_MISMATCH` | error/warning | Column dtype differs from baseline |
| `DRIFT_UNEXPECTED_NULLS` | warning | Non-nullable column contains NaN |
| `DRIFT_ROW_COUNT_LOW` | warning | Fewer rows than `min_rows` |
| `DRIFT_ROW_COUNT_HIGH` | warning | More rows than `max_rows` |
| `DRIFT_NO_BASELINE` | info | No baseline registered for this provider/dataset_type |

### Custom schemas

```python
from vnstock.core.provider.drift import DatasetSchema, ColumnSpec, register_schema

register_schema(DatasetSchema(
    dataset_type="my_type",
    provider="my_provider",
    columns=[ColumnSpec("price", "float64"), ColumnSpec("volume", "int64")],
    min_rows=1,
))
```

---

## Cross-Provider Comparison

Use `compare_ohlcv()` to find divergences between providers on the same symbol/interval.

```python
from vnstock.core.provider.compare import compare_ohlcv

report = compare_ohlcv(
    {"vci": vci_df, "kbs": kbs_df, "dnse": dnse_df},
    symbol="FPT",
    interval="1D",
    start="2026-01-01",
    end="2026-06-30",
)

print(report.comparable)        # True / False
print(report.price_diff_summary)
for issue in report.issues:
    print(issue.code, issue.message)
```

Issue codes:

| Code | Severity | Meaning |
|------|----------|---------|
| `COMPARE_INSUFFICIENT_PROVIDERS` | warning | Need at least 2 providers to compare |
| `COMPARE_COVERAGE_GAP` | warning | Provider missing ≥ 20 % of base-provider dates |
| `COMPARE_NO_COMMON_DATES` | error | No overlapping dates between providers |
| `COMPARE_PRICE_DIVERGENCE` | warning | Max close diff ≥ 1 % (configurable) |
| `COMPARE_PRICE_DIVERGENCE_HIGH` | error | Max close diff ≥ 5 % (configurable) |
| `COMPARE_VOLUME_DIVERGENCE` | warning | Max volume diff ≥ 10 % (configurable) |

---

## Health Scoring

Use `score_health()` to derive a `ProviderHealth` snapshot from collected evidence.

```python
from vnstock.core.provider.health import score_health, aggregate_health
from vnstock.core.provider.drift import detect_drift

drift_issues = detect_drift(df, "vci", "ohlcv")
health = score_health(
    "vci",
    drift_issues,
    latency_ms=250.0,
    error_rate=0.02,
    schema_status="ok",
    freshness_status="fresh",
    capabilities_checked=["ohlcv/equity", "price_board/equity"],  # list[str], optional
)

print(health.status)   # "healthy" | "degraded" | "failing" | "unknown"
print(health.to_json())
```

Status thresholds:

| Condition | Status |
|-----------|--------|
| Any error-severity issue | `failing` |
| `latency_ms >= 10000` | `failing` |
| `error_rate >= 0.50` | `failing` |
| Any warning-severity issue | `degraded` |
| `latency_ms >= 3000` | `degraded` |
| `error_rate >= 0.10` | `degraded` |
| Otherwise | `healthy` |

---

## Capability Matrix

```python
from vnstock.core.provider.matrix import build_matrix, render_matrix_text

matrix_dict = build_matrix(providers=["VCI", "KBS", "DNSE"])
print(render_matrix_text(matrix_dict))
```

Filter by provider, dataset_type, or asset_class:

```python
matrix_dict = build_matrix(
    providers=["VCI", "KBS"],
    dataset_types=["ohlcv", "intraday_trades"],
    asset_classes=["equity"],
)
```

---

## Contract Tests

Provider contract tests live under `tests/contracts/providers/`. They:

- Load stored JSON fixtures from `tests/fixtures/providers/{dnse,kbs,vci}/`
- Patch `send_request` to return the fixture (no live HTTP calls)
- Assert the adapter produces a normalized DataFrame with expected columns and dtypes

Run them with:

```bash
PYTHONPATH=. pytest tests/contracts/providers/ -v
```

They are included in the default CI suite (`tests/contracts/`).

---

## Live Smoke Tests

Live smoke tests verify real provider endpoints. They are **disabled by default** and excluded from normal CI.

### Location

```
tests/live/providers/
├── conftest.py            # env-var gating, provider/symbol filtering, auto-skip
├── test_dnse_live.py      # DNSE OHLCV, price board, intraday
├── test_kbs_live.py       # KBS OHLCV, price board
└── test_vci_live.py       # VCI OHLCV, price board
```

### Enabling live tests

```bash
VNSTOCK_LIVE_TESTS=true pytest tests/live/providers -m live -v
```

### Filtering by provider or symbol

```bash
# Only test DNSE
VNSTOCK_LIVE_TESTS=true VNSTOCK_LIVE_PROVIDERS=DNSE pytest tests/live/providers -m live

# Only test with FPT
VNSTOCK_LIVE_TESTS=true VNSTOCK_LIVE_SYMBOLS=FPT pytest tests/live/providers -m live
```

| Env var | Default | Description |
|---------|---------|-------------|
| `VNSTOCK_LIVE_TESTS` | `false` | Set to `true` to enable live tests |
| `VNSTOCK_LIVE_PROVIDERS` | `DNSE,KBS,VCI` | Comma-separated providers to test |
| `VNSTOCK_LIVE_SYMBOLS` | `FPT,VCB,TCB` | Comma-separated symbols to use |

### Safety rules

- Each test uses only the **first symbol** from `VNSTOCK_LIVE_SYMBOLS` to minimise request count.
- Date ranges are short (≤ 1 month) to avoid large responses.
- Tests that return empty data on non-trading days call `pytest.skip()` rather than failing.
- Never run live tests against real provider endpoints in normal CI pipelines.

### Scheduled / manual CI workflow

A separate GitHub Actions workflow (`.github/workflows/ci.yml`, job `live-smoke`) can run live tests on demand or on a schedule:

```bash
VNSTOCK_LIVE_TESTS=true PYTHONPATH=. pytest tests/live/providers -m live --tb=short
```

This workflow is triggered manually (`workflow_dispatch`) and is not required for PR merges.

---

## Fixtures

Stored raw API responses live under `tests/fixtures/providers/`:

```
tests/fixtures/providers/
├── README.md          # how to update fixtures
├── dnse/
│   ├── ohlcv_daily_raw.json
│   ├── price_board_raw.json
│   └── intraday_raw.json
├── kbs/
│   ├── ohlcv_daily_raw.json
│   ├── price_board_raw.json
│   └── intraday_raw.json
└── vci/
    ├── ohlcv_daily_raw.json
    ├── price_board_raw.json
    └── intraday_raw.json
```

To refresh a fixture, call the real endpoint with your preferred HTTP tool, save the raw JSON, and verify the contract tests still pass.

---

## Limitations

- Drift detection compares column names and dtype prefixes only; it does not check value ranges (use the quality layer for that).
- `detect_drift()` returns a `DRIFT_INVALID_INPUT` error issue (not a Python exception) when passed a non-DataFrame or empty provider string, ensuring it never raises.
- Comparison is currently implemented for OHLCV only; price board and intraday comparison are not yet implemented.
- `compare_ohlcv()` returns a `COMPARE_INVALID_INPUT` error issue when passed a non-dict or when any dict value is not a DataFrame.
- Health scoring is purely evidence-based (no live pings); callers must supply latency/error-rate from their own measurement.
- `score_health()` `capabilities_checked` parameter accepts `list[str] | None` (capability keys, e.g. `"ohlcv/equity"`). The legacy `int` form is no longer the intended API.
- `ProviderComparisonReport.issues` is typed as `List[ProviderIssue]`, not `List[str]`. Downstream code that treated issues as strings must be updated.
- Live smoke tests are not part of default CI and require external network access.
