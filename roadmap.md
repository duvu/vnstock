# vnstock Roadmap — Data Collection Foundation

> Goal: make `vnstock` a reliable **data extraction, validation, provider-diagnostics, and ingestion foundation** for Vietnamese and global market data research.
>
> Architecture constraint: **data-only**. No broker execution, no order placement, no account/portfolio APIs, no trading bots, no recommendation engine.

---

## Codebase Review — 2026-07-02

Current codebase already contains the first data-foundation layers:

- Unified UI over `Market`, `Reference`, `Fundamental`, and `Retail`
- KBS/VCI/DNSE support for core Vietnamese equity market paths
- cache layer with memory/SQLite backend
- data quality layer for OHLCV, price board, and intraday trades
- provider hardening layer with capability registry, drift detection, OHLCV comparison, health scoring, and matrix support
- provider contract fixtures/tests
- live smoke test scaffold gated by `VNSTOCK_LIVE_TESTS`
- CI for Ruff, format check, offline pytest, and build

The next priority is not scanner logic. The next priority is making data collection reliable, observable, and reproducible.

---

## Current State

### Implemented Foundation

| Area | Status | Notes |
|---|---:|---|
| Data-only package boundary | Done | Non-data APIs should remain outside core package. |
| Unified UI | Done | Main entrypoints are `Market`, `Reference`, `Fundamental`, `Retail`. |
| DNSE provider | Done | Adds OHLCV and price board coverage; intraday support is constrained. |
| Cache layer | Done | Memory/SQLite cache exists. Live-data TTL discipline still needs explicit policy. |
| Provider router | Partial | Round-robin + cooldown exists. Health-aware routing is not yet integrated. |
| Data quality layer | Done for market data | OHLCV, price board, intraday validators exist. Reference/fundamental contracts remain future work. |
| Provider hardening | Partial | Capability registry, contract tests, drift detection, health scoring, matrix, and OHLCV comparison exist. Expansion still needed. |
| Live smoke tests | Partial | Tests exist and are env-gated. A dedicated scheduled/manual workflow is not yet wired. |
| CI | Done for offline suite | Ruff, format, pytest, build. Live tests are outside default CI. |
| Foreign investor data | Partial | Snapshot/session fields exist in price board; historical time-series is not implemented. |

### Market Data Capabilities

| Capability | Providers | Status / Notes |
|---|---|---|
| OHLCV history 1m–1M | KBS, VCI, DNSE, MSN, FMP | Core capability available. Needs batch API and stronger comparison. |
| Multi-symbol price board | KBS, VCI, DNSE | Available. Contains foreign investor snapshot fields where provider returns them. |
| Intraday tick tape today-only | KBS, VCI, DNSE | Available where provider supports it. Historical tick replay still missing. |
| Foreign investor snapshot | KBS primarily; DNSE/VCI to verify | Fields include `foreign_buy_volume`, `foreign_sell_volume`, `foreign_room` where available. |
| Historical foreign flow | Not implemented | Needs endpoint discovery, schema, fixtures, quality contract. |
| Put-through session total | KBS | Available as session data, not a full analytical dataset yet. |
| Open interest snapshot | KBS derivatives | Snapshot only. Historical OI remains investigation item. |
| Vietnam sector/index OHLCV | VCI, KBS | Available. Historical index membership still needs work. |
| Fundamental/company data | KBS, VCI, FMarket | Available but not yet covered by quality contracts. |
| SSI provider | Not implemented | FastConnect Data is official but credentialed; iBoard public API needs discovery. |
| ABS provider | Not implemented | Public priceboard is only a discovery candidate. |

### Remaining Risks

| Risk | Impact | Roadmap Response |
|---|---|---|
| Router does not consume provider health | Runtime may still select degraded providers until failure occurs | Phase 1 |
| Live smoke tests are manual only | Provider API drift may not be detected operationally | Phase 1 |
| `compare_ohlcv()` is OHLCV-only | Price board/intraday provider disagreements are not yet measurable | Phase 1 |
| No first-class rate limiter | Batch scans can hit provider limits | Phase 2 |
| No batch result envelope | Full-market scans cannot report partial failures cleanly | Phase 2 |
| Cache can mask stale live data | Intraday/price board collection may consume stale data | Phase 2 |
| No raw archive | Provider schema changes cannot be replayed/reparsed easily | Phase 2 |
| No persistent storage/sync | Reproducibility and auditability are limited | Phase 3 |
| Reference/fundamental validators are missing | Non-price data remains less safe | Phase 5 |

---

## Roadmap

## Phase 0 — Foundation Stabilization

**Status:** mostly complete.

Completed:

- data-only boundary
- global quality config honored by dispatch
- index-safe validation issue reporting
- internal validation failure diagnostics
- freshness datetime coercion
- provider model type fixes
- provider drift invalid-input guard
- provider comparison invalid-input guard
- offline provider contract tests
- live smoke test scaffold

Remaining polish:

- add explicit required-column preflight in `compare_ohlcv()` before accessing `time`, `close`, or `volume`
- remove unused internal accumulators in comparison code if they remain unused
- resolve stale doc references and old upstream marketing copy
- ensure docs describe current capabilities rather than planned capabilities

Exit criteria:

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest -m "not slow" tests/unit/core tests/unit/ui tests/unified_ui tests/contracts
PYTHONPATH=. pytest tests/unit/core/quality tests/unit/core/provider tests/contracts/providers -q
python -m build --sdist --wheel --no-isolation
```

---

## Phase 1 — Provider Reliability Completion

**Goal:** make providers interchangeable with measurable reliability.

### 1.1 Health-aware routing / diagnostics

Current router is round-robin with cooldown. Next step:

- prefer healthy providers
- use degraded providers as fallback
- skip failing providers unless `source=` is forced
- expose provider diagnostics in `df.attrs` or batch result metadata
- keep cooldown behavior for runtime failures and rate limits

### 1.2 Live smoke workflow

Live tests exist but need operational workflow support:

```bash
VNSTOCK_LIVE_TESTS=true PYTHONPATH=. pytest tests/live/providers -m live --tb=short
```

Add separate workflow:

- `workflow_dispatch`
- optional schedule
- provider/symbol filters
- artifact/report with provider status
- not required for normal PR merge

### 1.3 Cross-provider comparison expansion

Current comparison supports OHLCV. Add:

- price board comparison
- intraday trade shape comparison
- provider-specific tolerance profiles
- price-scale detection
- coverage/freshness comparison

### 1.4 Contract fixture expansion

Add edge fixtures:

- empty but valid response
- invalid symbol
- suspended symbol
- newly listed symbol
- non-trading day
- partial intraday session
- missing optional fields
- unexpected extra fields

Exit criteria:

- provider matrix reflects capabilities and testability
- offline fixtures cover core edge cases
- live smoke workflow can be run manually
- router behavior is tested with healthy/degraded/failing providers

---

## Phase 2 — Ingestion Runtime

**Goal:** support safe full-market collection without uncontrolled provider calls.

### 2.1 Rate limiter

Add provider-scoped throttling:

- in-memory token bucket or sliding-window limiter first
- per-provider/per-endpoint config
- 429 handling with cooldown integration
- jittered retry/backoff
- metrics hooks: request count, latency, error count, throttle count

Suggested env config:

```bash
VNSTOCK_RATE_LIMIT_ENABLED=true
VNSTOCK_RATE_LIMIT_KBS_PER_MINUTE=60
VNSTOCK_RATE_LIMIT_VCI_PER_MINUTE=60
VNSTOCK_RATE_LIMIT_DNSE_PER_MINUTE=60
```

### 2.2 Batch OHLCV API

Target API:

```python
result = Market().equity().history_batch(
    symbols=["FPT", "VCB", "TCB"],
    start="2024-01-01",
    end="2024-06-30",
    interval="1D",
    source="auto",
    validate=True,
    fail_fast=False,
)
```

Return a structured envelope:

```python
@dataclass
class BatchResult:
    data: dict[str, pd.DataFrame]
    errors: dict[str, Exception | str]
    quality: dict[str, ValidationReport]
    provider_used: dict[str, str]
    diagnostics: dict[str, Any]
```

### 2.3 Raw response archive

Persist raw provider responses before normalization:

```text
raw/provider=KBS/dataset=ohlcv/symbol=FPT/date=2026-07-02.json
normalized/provider=KBS/dataset=ohlcv/symbol=FPT/interval=1D.parquet
```

This allows reparse/revalidation when provider schema changes.

### 2.4 Cache policy for live vs historical data

| Data type | Default cache policy |
|---|---|
| Historical daily OHLCV | cache allowed |
| Reference/fundamental data | cache allowed |
| Price board | cache off or very short TTL |
| Intraday trades today | cache off or very short TTL |
| Live watcher events | cache off by default |

Exit criteria:

- full-market OHLCV scan can run with bounded provider calls
- partial failures are structured and inspectable
- provider and quality metadata exist per symbol
- raw and normalized outputs can be persisted together

---

## Phase 3 — Storage and Incremental Sync

**Goal:** make data collection reproducible and auditable.

### 3.1 Local storage sinks

- Parquet partitioned by dataset/symbol/interval/date
- DuckDB for local analytics
- SQLite metadata store for sync state

### 3.2 PostgreSQL / TimescaleDB sink

Target normalized OHLCV table:

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
    quality_report_json,
    provider_diagnostics_json,
    PRIMARY KEY(symbol, time, interval, provider)
)
```

### 3.3 Incremental sync

- sync by symbol/date range
- gap detection before fetch
- idempotent upsert
- revalidation without refetching raw data
- run manifest per sync job

Exit criteria:

- historical OHLCV can be synced incrementally
- re-runs are idempotent
- data lineage is traceable by provider and fetch timestamp
- quality reports are stored with the data

---

## Phase 4 — Dataset Coverage Expansion

**Goal:** expand collected datasets after runtime/storage foundations are stable.

Priority datasets:

1. OHLCV daily/intraday coverage expansion
2. price board snapshots
3. intraday trades
4. foreign investor flow
5. index/sector data
6. reference/company metadata
7. fundamental statements
8. corporate events
9. ownership/shareholders
10. derivatives/open interest if reliable

### 4.1 Foreign flow dataset

Current state:

- price board can expose `foreign_buy_volume`, `foreign_sell_volume`, and `foreign_room`
- historical foreign-flow time-series is not implemented

Target schema:

```text
symbol
date
foreign_buy_volume
foreign_sell_volume
foreign_net_volume
foreign_buy_value
foreign_sell_value
foreign_net_value
foreign_room
provider
fetched_at
```

Implementation should start only after endpoint discovery and raw fixtures are available.

---

## Phase 5 — Quality Contracts Beyond Market Data

**Goal:** apply quality validation to non-price datasets.

### 5.1 Reference data contracts

Validate:

- equity list
- industry list
- company info
- officers
- shareholders
- subsidiaries
- corporate events/news metadata

### 5.2 Fundamental data contracts

Validate:

- balance sheet
- income statement
- cash flow
- ratios
- period/fiscal-year consistency
- duplicate periods
- missing core line items
- unit scale consistency

Exit criteria:

- reference/fundamental outputs have schema contracts
- quality reports exist for non-price datasets
- provider drift is detectable for fundamental data

---

## Phase 6 — Intraday and Near-Real-Time Collection

**Goal:** collect intraday data safely without pretending to have exchange-grade streaming.

### 6.1 Session-aware polling

- market session calendar
- pre-open/continuous/ATC/post-close handling
- heartbeat/status events
- rate limiter integration
- provider fallback integration

### 6.2 Append-only intraday storage

- snapshot deduplication
- trade id deduplication
- stale detection
- polling manifest
- provider diagnostics per event batch

Exit criteria:

- near-real-time collection loop can run safely
- rate limits are respected
- stale/invalid data is surfaced explicitly

---

## Phase 7 — Data Catalog, Lineage, and Observability

**Goal:** make collected data understandable and operationally visible.

Add:

- dataset catalog
- provider capability catalog
- schema registry
- sync run manifest
- freshness dashboard
- quality dashboard
- provider uptime/error dashboard
- data coverage report

Exit criteria:

- every dataset has owner/source/schema/freshness metadata
- every sync job has a manifest
- operational health is visible without reading raw logs

---

## Phase 8 — Scanner / Research Readiness

**Goal:** prepare validated and auditable inputs for pattern detection and AI-assisted research.

Scanner work should start after data collection is reliable.

Inputs should include:

- clean symbol universe
- listing status
- exchange/sector metadata
- OHLCV bars
- liquidity/turnover/value features
- foreign-flow features where available
- relative strength vs index/sector
- quality summary and exclusion reasons

Exit criteria:

- scanner consumes validated datasets only
- every excluded symbol has a machine-readable reason
- run manifests include code version, data version, provider diagnostics, and quality summary

---

## Priority Matrix

```text
  High Impact
     │
     │   P1 provider reliability ── next blocker
     │   P2 ingestion runtime ───── batch, retry, rate-limit, raw archive
     │   P3 storage/sync ────────── reproducibility and auditability
     │   P4 coverage expansion ──── collect more datasets
     │
     │   P5 quality contracts ───── trust beyond market data
     │   P6 intraday collection ─── near-real-time pipeline
     │   P7 catalog/observability ─ operate the platform
     │   P8 scanner readiness ───── research layer after data is solid
     │
     └────────────────────────────────────────────────────────────
          Lower Effort ───────────────────────────── Higher Effort
```

**Start here:** Phase 1 provider reliability, then Phase 2 ingestion runtime.

**Architectural rule:** quality reports and provider diagnostics must travel with the data. Do not let downstream scanners consume anonymous, unvalidated DataFrames.

---

## Definition of Done for Data Collection Foundation

The data foundation is ready when:

- provider health is reflected in routing or batch diagnostics
- batch API reports partial failures cleanly
- rate limiting prevents uncontrolled provider calls
- raw responses can be archived
- normalized outputs carry provider metadata
- quality reports attach to every validated dataset
- storage persists quality and provider diagnostics
- full-market scans are reproducible and auditable
- live smoke checks can be run operationally

---

*Last updated: 2026-07-02*
