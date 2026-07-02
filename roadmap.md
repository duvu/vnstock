# vnstock Roadmap — Data-Only Market Data Layer

> Goal: make `vnstock` a first-class **data extraction and validation library** for Vietnamese and global market data research.
>
> Architecture constraint: **data extraction only**. No user registration, no broker execution, no order placement, no portfolio management, no trading strategy engine.

---

## Roadmap Review — 2026-07-02

Recent implementation added two major foundations:

1. **Data Quality Layer** — schema, numeric, temporal, freshness, OHLCV, price board, and intraday validation.
2. **Provider Hardening Layer** — capability registry, contract fixtures/tests, schema drift detection, cross-provider OHLCV comparison, health scoring, and capability matrix.

CI now passes for Ruff, format, pytest, and build across Python 3.10–3.13. However, code review identified correctness issues that must be fixed before building scanner, batch, watcher, or storage features on top of these layers.

The roadmap is therefore updated to prioritize **correctness and runtime robustness before new trading-data capabilities**.

---

## Current State

### Implemented / In Progress

| Area | Status | Notes |
|---|---:|---|
| Data-only package boundary | Done | Non-data APIs are being removed/deprecated from the package scope. |
| DNSE provider | Done | Adds OHLCV, price board, and intraday coverage as a third Vietnam market provider. |
| Cache layer | Done | In-process / SQLite cache with TTL controls. Needs live-data TTL discipline. |
| Provider router | Done | Round-robin and failover foundation. Health-aware routing still needs correction/follow-up. |
| Data quality layer | Implemented, needs correctness fixes | Core validators exist but edge cases need fixing before production use. |
| Provider hardening layer | Implemented, needs correctness fixes | Core models/tests exist but type contracts and invalid-input guards need fixing. |
| CI | Done | Ruff, format, pytest, build across Python 3.10–3.13. |

### Market Data Capabilities

| Capability | Providers | Notes |
|---|---|---|
| OHLCV history 1m–1M | KBS, VCI, DNSE, MSN, FMP | KBS/DNSE native intervals; VCI may resample some intervals. |
| Multi-symbol price board | KBS, VCI, DNSE | VCI has richer bid/ask depth; KBS has 3-level BBO. |
| Intraday tick tape today-only | KBS, VCI, DNSE | Historical tick replay still not available. |
| Match type classification | KBS, VCI, DNSE | Needs standardized contract and provider comparison. |
| Foreign flow session total | KBS, DNSE | Session totals only; time-series still missing. |
| Put-through trades session total | KBS | Negotiated block trade qty/value. |
| Open interest snapshot | KBS derivatives | Today only; no history. |
| Forex/crypto OHLCV | MSN, FMP | Global market support, not Vietnam-specific. |
| Vietnam sector/index OHLCV | VCI, KBS | VCI broader sector index coverage. |
| Fundamental/company data | KBS, VCI, FMarket | Needs quality contracts later. |

### Known Risks

| Risk | Impact | Roadmap Response |
|---|---|---|
| Quality validation can be skipped despite global env config | Users may think validation is active when it is not | Phase 0 correctness fix |
| Validators assume integer index labels | Real OHLCV DataFrames with `DatetimeIndex` can crash validation | Phase 0 correctness fix |
| Internal validation errors may be swallowed silently | Bad data may pass downstream without diagnostics | Phase 0 correctness fix |
| Freshness metadata may be serialized as string | Freshness check can crash on `df.attrs["fetched_at"]` | Phase 0 correctness fix |
| Provider hardening type mismatches | Static analysis and downstream consumers see inconsistent API | Phase 0 correctness fix |
| Contract tests may skip on adapter drift | CI may miss broken provider interfaces | Phase 0 correctness fix |
| Live endpoint compatibility not tested by default | Fixture tests can pass while real provider APIs drift | Phase 1 live smoke checks |

---

## Updated Roadmap

## Phase 0 — Correctness Stabilization Gate

**Goal:** make the newly added data quality and provider hardening layers safe enough to depend on.

**Status:** Required before any new feature work.

### 0.1 Fix global quality config

- `VNSTOCK_QUALITY_ENABLED=true` must enable validation without requiring per-call `validate=True`.
- `VNSTOCK_QUALITY_MODE` must be used when `quality_mode` is not supplied.
- Explicit call kwargs must override global config.

### 0.2 Make validators index-safe

- Remove all unsafe `row_index=int(idx)` patterns.
- Store `row_index` as 0-based positional offset.
- Store original index label in `context["index_label"]` when useful.
- Add regression tests for `DatetimeIndex`, string index, and non-default indexes.

### 0.3 Make validation failures observable

- Do not silently swallow unexpected validation exceptions.
- In warn mode, attach a synthetic report with `QUALITY_VALIDATION_INTERNAL_ERROR`.
- In strict mode, raise or wrap the internal validation error.

### 0.4 Harden freshness and timezone handling

- Parse `fetched_at` when it is a string.
- Normalize freshness comparisons to UTC-aware datetimes.
- Convert timezone-aware intraday timestamps to `Asia/Ho_Chi_Minh` before session validation.

### 0.5 Fix provider type contracts

- `ProviderComparisonReport.issues` must be `list[ProviderIssue]`.
- `score_health(..., capabilities_checked=...)` must use `list[str]`, not `int`.
- Ensure serialization works for all provider models.

### 0.6 Add provider invalid-input guards

- `detect_drift(None, ...)` should return `DRIFT_INVALID_INPUT`, not crash.
- `compare_ohlcv()` should return `COMPARE_INVALID_INPUT` for invalid input.
- Missing required OHLCV columns should produce a structured issue.

### 0.7 Make contract tests fail on adapter drift

- Remove broad `try/except Exception: pytest.skip(...)` from offline provider contract tests.
- Offline contract tests should fail when provider module path or method signature changes.

### Exit Criteria

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest -m "not slow" tests/unit/core tests/unit/ui tests/unified_ui tests/contracts
PYTHONPATH=. pytest tests/unit/core/quality tests/unit/core/provider tests/contracts/providers -q
python -m build --sdist --wheel --no-isolation
```

No unresolved high-priority review findings should remain.

---

## Phase 1 — Provider Hardening Completion

**Goal:** make providers interchangeable with measurable reliability.

**Depends on:** Phase 0.

### 1.1 Provider contract fixture coverage

- Expand fixture coverage for KBS, VCI, DNSE.
- Include edge fixtures:
  - empty but valid response
  - suspended symbol
  - newly listed symbol
  - holiday/no trading day
  - partial intraday session
  - missing optional fields

### 1.2 Live smoke tests

- Add opt-in live smoke tests gated by env vars:

```bash
VNSTOCK_LIVE_TESTS=true
VNSTOCK_LIVE_PROVIDERS=DNSE,KBS,VCI
VNSTOCK_LIVE_SYMBOLS=FPT,VCB,TCB
```

- Keep live tests out of normal CI.
- Add manual or scheduled workflow for live provider compatibility checks.

### 1.3 Cross-provider comparison expansion

Current comparison focuses on OHLCV. Expand to:

- price board snapshots
- intraday trades
- foreign flow session totals where available

### 1.4 Health-aware router

- Router should prefer healthy providers.
- Degraded providers should be fallback-only.
- Failing providers should be skipped unless caller explicitly forces source.

### Exit Criteria

- Provider capability matrix generated.
- Contract tests pass offline.
- Live smoke tests can be run manually without changing code.
- Router behavior is covered by tests.

---

## Phase 2 — Batch and Rate-Limit Foundations

**Goal:** support full-market scans without uncontrolled provider calls.

**Depends on:** Phase 0 and core parts of Phase 1.

### 2.1 Rate-limit / throttle manager

- Add provider-scoped token bucket or sliding-window rate limiter.
- Support memory backend first.
- Add Redis backend later if multiple workers are needed.
- Config via `VNSTOCK_RATE_LIMIT_*`.

### 2.2 Batch OHLCV API

Target API:

```python
result = Market().equity().history_batch(
    symbols=["FPT", "VCB", "TCB"],
    start="2025-01-01",
    end="2026-07-02",
    interval="1D",
    source="auto",
    validate=True,
    fail_fast=False,
)
```

Return should include:

- data by symbol
- per-symbol errors
- provider used
- validation summary
- retry/fallback summary

### 2.3 Multi-day intraday OHLCV chunker

- Auto-split long intraday date ranges into provider-safe windows.
- Stitch results and de-duplicate timestamps.
- Attach validation and provider diagnostics.

### Exit Criteria

- Full-market daily OHLCV scan can run with bounded provider calls.
- Partial failures are reported without crashing entire batch.
- Quality reports are available per symbol.

---

## Phase 3 — Scanner Data Readiness

**Goal:** prepare clean, validated data for pattern detection and AI-assisted research.

**Depends on:** Phase 0 and Phase 2.

### 3.1 Universe snapshot

- Add a clean universe loader for HOSE, HNX, UPCOM.
- Include listing status, exchange, industry/sector if available.
- Mark suspended/delisted/new listings explicitly.

### 3.2 Feature-ready normalized outputs

Standardize outputs for scanner features:

- OHLCV bars
- liquidity metrics
- turnover/value
- foreign flow
- relative strength vs VNINDEX/VN30/sector index
- accumulation/base metrics
- breakout candidate features

### 3.3 Data quality summary report

For each scanner run, generate:

- symbol coverage
- missing dates
- stale data
- provider fallback usage
- validation warnings/errors
- excluded symbols and reasons

### Exit Criteria

- Scanner input dataset can be trusted and audited.
- Every excluded symbol has a machine-readable reason.
- No signal generation is run on unvalidated data by default.

---

## Phase 4 — Storage and Incremental Sync

**Goal:** turn the library into a reliable ingestion component for research pipelines.

**Depends on:** Phase 0, Phase 1, Phase 2.

### 4.1 Local storage sinks

- Parquet sink
- DuckDB sink
- SQLite metadata store for sync state

### 4.2 TimescaleDB/PostgreSQL sink

Target table:

```sql
market_ohlcv(
    symbol,
    time,
    interval,
    open,
    high,
    low,
    close,
    volume,
    provider,
    fetched_at,
    quality_status,
    PRIMARY KEY(symbol, time, interval, provider)
)
```

### 4.3 Incremental sync

- Sync by symbol/date range.
- Idempotent upsert.
- Store provider diagnostics and validation summaries.
- Allow revalidation without refetching raw data.

### Exit Criteria

- Historical OHLCV can be synced incrementally.
- Re-runs are idempotent.
- Data lineage is traceable by provider and fetch timestamp.

---

## Phase 5 — Live Watcher / Polling Adapter

**Goal:** provide stream-like polling without pretending to have WebSocket support.

**Depends on:** Phase 0, Phase 1, Phase 2.

### 5.1 Watcher class

Target API:

```python
watcher = Market().equity().watcher(
    symbols=["VCB", "TCB"],
    interval_seconds=3,
    source="auto",
    validate=True,
)

for event in watcher.stream():
    process(event)
```

### 5.2 Session-aware polling

- Do not poll aggressively outside market hours.
- Support pre-open, continuous session, ATC, post-close behavior.
- Emit heartbeat/status events.

### 5.3 Live diagnostics

Each event should include:

- provider used
- latency
- cache hit/miss
- validation summary
- stale flag
- retry/fallback count

### Exit Criteria

- Watcher can run a paper scanner loop safely.
- Rate limits are respected.
- Stale or invalid data is surfaced explicitly.

---

## Phase 6 — Additional Trading Data Coverage

**Goal:** close useful market-data gaps after the data foundation is reliable.

**Depends on:** earlier phases.

### 6.1 Volume-by-price

- Wire KBS matched-by-price endpoint if still available.
- Return price, buy volume, sell volume, unknown volume, total volume.

### 6.2 Historical foreign flow

- Investigate available endpoints for daily foreign buy/sell/net flow.
- Add time-series support only if reliable and contract-tested.

### 6.3 Level 2 order book normalization

- Extract VCI bid/ask ladder from existing price board.
- Normalize to side/level/price/volume schema.

### 6.4 Open interest history

- Investigate futures OI history endpoints.
- Add only if source is stable enough for contract/live smoke coverage.

### 6.5 Index membership history

- Investigate sector/index constituent endpoints.
- Required for proper historical relative-strength and sector rotation studies.

---

## Priority Matrix

```text
  High Impact
     │
     │   P0 correctness fixes ───── mandatory gate before downstream use
     │   P1 provider hardening ──── makes source fallback trustworthy
     │   P2 rate limit + batch ──── unlocks full-market scanning
     │   P3 scanner readiness ───── clean input for pattern detection
     │
     │   P4 storage sync ────────── research-grade ingestion layer
     │   P5 watcher ─────────────── live/paper scanner loop
     │   P6 extra endpoints ─────── useful but must wait for foundation
     │
     └────────────────────────────────────────────────────────────
          Low Effort ─────────────────────────────── High Effort
```

**Start here:** Phase 0. Do not build scanner, batch, watcher, or storage on top of validators/provider hardening until correctness fixes land.

**Biggest unlock after Phase 0:** Phase 2 batch + rate limiting. This enables full-market scans without provider abuse.

**Most important architectural rule:** data quality and provider diagnostics must travel with the data. A scanner should never consume anonymous, unvalidated DataFrames.

---

## Provider Capability Matrix — Current

| Capability | KBS | VCI | DNSE | MSN | FMP | FMarket |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Intraday OHLCV 1m | yes | yes/resample | yes | no | yes/global | no |
| Intraday OHLCV 5m/15m/30m | yes | resample | yes | no | yes/global | no |
| Intraday OHLCV 1h | yes | yes | yes | no | yes/global | no |
| Daily/Weekly/Monthly OHLCV | yes | yes | yes | yes | yes | no |
| Tick tape today-only | yes | yes | yes | no | no | no |
| Historical tick data | no | no | no | no | no | no |
| Price board multi-symbol | yes | yes | yes | no | no | no |
| Foreign flow session | yes | partial | yes | no | no | no |
| Foreign flow time-series | stub/unknown | unknown | unknown | no | no | no |
| Volume-by-price | stub | no | no | no | no | no |
| Level 2 order book | partial | in price_board | unknown | no | no | no |
| Open interest today | yes/futures | unknown | unknown | no | no | no |
| Open interest history | unknown | unknown | unknown | no | no | no |
| Fundamental/company data | yes | yes | no | no | no | yes |
| Forex/crypto OHLCV | no | no | no | yes | yes | no |
| Vietnam sector indices | yes/limited | yes/broad | unknown | no | no | no |
| WebSocket/streaming | no | no | no | no | no | no |

---

## Definition of Done for Data Foundation

The data foundation is considered ready for scanner development only when:

- quality validation can be globally enabled and verified
- validators are index-safe
- validation failures are observable
- provider model type contracts are consistent
- provider drift/comparison functions handle invalid input safely
- contract tests fail on adapter drift
- offline CI passes on Python 3.10–3.13
- live smoke checks are available for manual/scheduled runs
- data quality reports and provider diagnostics are attached to returned data or batch reports

---

*Last updated: 2026-07-02*
