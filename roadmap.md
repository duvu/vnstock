# vnstock Roadmap — Data-Only Market Data Layer

> Goal: make `vnstock` a first-class **data extraction, validation, and provider-diagnostics library** for Vietnamese and global market data research.
>
> Architecture constraint: **data extraction only**. No broker execution, no order placement, no portfolio management, no recommendation engine, and no automated trading strategy engine.

---

## Codebase Review — 2026-07-02

The codebase has moved beyond the earlier roadmap. The foundational data layer now exists and the immediate correctness fixes have been implemented.

Recent merged work includes:

- data quality layer for OHLCV, price board, and intraday trade validation
- provider hardening package with capability registry, drift detection, OHLCV comparison, provider health scoring, provider models, and capability matrix
- provider contract fixtures/tests for DNSE, KBS, and VCI
- live smoke test scaffold gated by `VNSTOCK_LIVE_TESTS`
- correctness fixes for global quality config, index-safe validators, freshness datetime parsing, provider type contracts, and invalid-input handling
- CI with Ruff, format, pytest, and build across Python 3.10–3.13

The roadmap is therefore updated again: **Phase 0 is no longer the main blocker**. The next bottleneck is provider reliability completion and batch/rate-limit infrastructure.

---

## Current State

### Implemented Foundation

| Area | Status | Notes |
|---|---:|---|
| Data-only package boundary | Done | Package direction is data extraction only. Non-data/broker features should stay out of core. |
| DNSE provider | Done | Adds OHLCV, price board, and intraday coverage alongside KBS and VCI. |
| Cache layer | Done | Memory/SQLite cache exists. Live-data TTL discipline still needs careful defaults. |
| Provider router | Partial | Round-robin + failure cooldown exists. Health-aware routing is not yet integrated. |
| Data quality layer | Done for market data | OHLCV, price board, intraday validators exist. Reference/fundamental quality contracts remain future work. |
| Quality correctness fixes | Done | Global env config, index-safe rows, freshness parsing, internal validation diagnostics fixed. |
| Provider hardening | Partial | Capability registry, contract tests, drift detection, health scoring, matrix, and OHLCV comparison exist. Expansion still needed. |
| Live smoke tests | Partial | Tests exist and are env-gated. A dedicated scheduled/manual workflow is still not wired into CI. |
| CI | Done for offline suite | Ruff, format, pytest, and build run in CI. Live provider tests are intentionally outside default CI. |

### Market Data Capabilities

| Capability | Providers | Status / Notes |
|---|---|---|
| OHLCV history 1m–1M | KBS, VCI, DNSE, MSN, FMP | Core capability available. Needs batch API and stronger cross-provider comparison. |
| Multi-symbol price board | KBS, VCI, DNSE | Available. Needs normalized comparison and quality summary across providers. |
| Intraday tick tape today-only | KBS, VCI, DNSE | Available for current-day data. Historical tick replay still missing. |
| Match type classification | KBS, VCI, DNSE | Available but should be contract-tested more deeply across edge sessions. |
| Foreign flow session total | KBS, DNSE | Session-level data available. Historical foreign-flow time-series still missing. |
| Put-through trades session total | KBS | Available as session total; needs stable normalized contract if used downstream. |
| Open interest snapshot | KBS derivatives | Snapshot only. Historical OI remains investigation item. |
| Forex/crypto OHLCV | MSN, FMP | Available for global market data. Not central to Vietnam equity scanner MVP. |
| Vietnam sector/index OHLCV | VCI, KBS | Available. Need index membership/sector mapping for correct relative-strength features. |
| Fundamental/company data | KBS, VCI, FMarket | Available but not yet covered by the new quality layer. |

### Remaining Risks After Latest Fixes

| Risk | Impact | Roadmap Response |
|---|---|---|
| Router does not consume provider health | Router may select degraded/failing providers until runtime failure occurs | Phase 1 |
| `compare_ohlcv()` is OHLCV-only and still needs stricter schema preflight | Provider comparison is useful but not yet general or fully defensive | Phase 1 |
| Live smoke tests are not in a dedicated workflow | Manual live verification is possible but not operationalized | Phase 1 |
| Cache can mask stale live data if used incorrectly | Scanner/watchers may consume old snapshots | Phase 2 |
| No first-class rate limiter | Batch scans/watchers can hit provider limits | Phase 2 |
| No batch result envelope | Full-market scans cannot report partial failures cleanly | Phase 2 |
| No persistent storage/incremental sync | Repeated scans re-fetch data and make reproducibility harder | Phase 3 |
| Reference/fundamental validators are not implemented | Non-price data remains less safe for downstream analytics | Phase 5 |

---

## Updated Roadmap

## Phase 0 — Foundation Stabilization

**Status: mostly complete.**

**Goal:** ensure the new data quality and provider hardening layers are safe enough to depend on.

Completed:

- Global quality config is honored by `BaseUI._dispatch()`.
- `validate` and `quality_mode` no longer leak to provider calls.
- Validators no longer assume integer index labels.
- `row_index` is treated as positional offset.
- Internal validation failures are observable via `QUALITY_VALIDATION_INTERNAL_ERROR`.
- Freshness parsing supports `datetime`, `pd.Timestamp`, and ISO strings.
- Intraday session validation converts timezone-aware timestamps to Vietnam local time.
- Provider comparison report uses `ProviderIssue` objects.
- Provider health uses `capabilities_checked: list[str]`.
- Drift/comparison utilities have invalid-input guards.
- Offline contract tests should fail on adapter drift instead of silently skipping.

Remaining polish:

- Add explicit required-column preflight in `compare_ohlcv()` before accessing `df["time"]`, `close`, or `volume`.
- Remove unused internal accumulators in `compare_ohlcv()` if they are not returned.
- Align `docs/PROVIDER_HARDENING.md` with actual live test paths and CI behavior.
- Confirm all old review threads are resolved or intentionally dismissed.

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

**Status: next priority.**

**Goal:** make provider fallback and diagnostics trustworthy enough for full-market ingestion.

### 1.1 Health-aware router integration

Current router is round-robin with cooldown. It should become health-aware:

- prefer providers with `ProviderHealth.status == "healthy"`
- use degraded providers only when no healthy provider is available
- skip failing providers unless caller forces `source=`
- expose provider diagnostics in `df.attrs` or batch result metadata
- keep the current cooldown behavior for runtime failures and 429s

### 1.2 Live smoke workflow

Live smoke tests exist but should be operationalized:

```bash
VNSTOCK_LIVE_TESTS=true PYTHONPATH=. pytest tests/live/providers -m live --tb=short
```

Add a separate workflow, not required for normal PR merge:

- `workflow_dispatch` for manual live checks
- optional scheduled run outside market close periods
- provider/symbol filters through env vars
- artifact/report summarizing provider status

### 1.3 Cross-provider comparison expansion

Current comparison focuses on OHLCV. Expand to:

- price board snapshot comparison
- intraday trade shape comparison
- session foreign-flow comparison where available
- provider-specific tolerance profiles
- price scale detection across providers

### 1.4 Contract fixture expansion

Add fixtures for edge cases:

- empty but valid response
- invalid symbol
- suspended symbol
- newly listed symbol
- non-trading day
- partial intraday session
- provider returns optional fields missing
- provider returns extra unexpected fields

Exit criteria:

- provider matrix generated from declared capabilities and test status
- offline contract tests cover edge fixtures
- live smoke workflow can be run manually
- router selection is test-covered with healthy/degraded/failing providers

---

## Phase 2 — Batch and Rate-Limit Foundations

**Goal:** support full-market scans without uncontrolled provider calls.

**Depends on:** Phase 0 and the critical subset of Phase 1.

### 2.1 Provider rate limiter

Add a provider-scoped rate limiter before adding high-volume batch APIs.

Initial scope:

- in-memory token bucket or sliding window
- per-provider/per-endpoint configuration
- 429 handling with cooldown integration
- jittered retry/backoff policy
- metrics hooks for request count, error count, and throttle count

Configuration proposal:

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
    start="2025-01-01",
    end="2026-07-02",
    interval="1D",
    source="auto",
    validate=True,
    fail_fast=False,
)
```

Return a structured batch result rather than only `dict[str, DataFrame]`:

```python
@dataclass
class BatchResult:
    data: dict[str, pd.DataFrame]
    errors: dict[str, Exception | str]
    quality: dict[str, ValidationReport]
    provider_used: dict[str, str]
    diagnostics: dict[str, Any]
```

### 2.3 Cache policy for live vs historical data

Define explicit cache behavior:

| Data type | Default cache policy |
|---|---|
| Historical daily OHLCV | cache allowed |
| Fundamental/reference data | cache allowed |
| Price board | cache off or very short TTL |
| Intraday trades today | cache off or very short TTL |
| Live watcher events | cache off by default |

Exit criteria:

- full-market daily OHLCV scan can run with bounded provider calls
- partial failures are reported without crashing the whole batch
- every symbol has provider + validation metadata
- cache cannot silently serve stale live snapshots into scanner flow

---

## Phase 3 — Storage and Incremental Sync

**Goal:** turn `vnstock` into a reliable ingestion component for research pipelines.

**Depends on:** Phase 2.

### 3.1 Local research storage

Add lightweight sinks first:

- Parquet partitioned by dataset/symbol/interval/date
- DuckDB for local analytics
- SQLite metadata store for sync state

### 3.2 TimescaleDB/PostgreSQL sink

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
- idempotent upsert
- gap detection before fetch
- revalidation without refetching raw data
- sync manifest/report per run

Exit criteria:

- historical OHLCV can be synced incrementally
- re-runs are idempotent
- data lineage is traceable by provider and fetch timestamp
- quality reports are stored with the data

---

## Phase 4 — Scanner Data Readiness

**Goal:** prepare validated, auditable inputs for pattern detection and AI-assisted research.

**Depends on:** Phase 2 and preferably Phase 3.

### 4.1 Universe snapshot

- clean universe loader for HOSE, HNX, UPCOM
- listing status, exchange, industry/sector if available
- mark suspended, delisted, newly listed symbols explicitly
- exclude or flag symbols with insufficient history

### 4.2 Feature-ready normalized outputs

Standardize feature inputs for:

- OHLCV bars
- liquidity/turnover/value
- rolling volume profile
- volatility and gap metrics
- foreign-flow features where available
- relative strength vs VNINDEX/VN30/sector index
- accumulation/base metrics
- breakout candidate features

### 4.3 Data quality summary report

Every scanner run should produce:

- universe coverage
- missing dates
- stale data
- provider fallback usage
- validation warnings/errors
- excluded symbols and reasons
- run manifest with code version and config

Exit criteria:

- scanner input dataset can be trusted and audited
- every excluded symbol has a machine-readable reason
- no scanner consumes unvalidated data by default

---

## Phase 5 — Extend Quality Contracts Beyond Market Data

**Goal:** apply the same quality discipline to reference and fundamental data.

**Depends on:** Phase 0 and Phase 1.

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
- financial ratios
- period/fiscal-year consistency
- missing line items
- duplicate periods
- unit scale consistency

### 5.3 Provider comparison for fundamentals

Where providers overlap, compare:

- period coverage
- unit scale
- core financial fields
- reporting date consistency

Exit criteria:

- non-price datasets have schema contracts
- quality reports exist for reference/fundamental outputs
- provider drift is detectable for fundamental data

---

## Phase 6 — Live Watcher / Polling Adapter

**Goal:** provide stream-like polling without pretending to have WebSocket support.

**Depends on:** Phase 1 and Phase 2.

### 6.1 Watcher class

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

### 6.2 Session-aware polling

- do not poll aggressively outside market hours
- support pre-open, continuous session, ATC, and post-close behavior
- emit heartbeat/status events
- apply rate limiter and health-aware provider selection

### 6.3 Live diagnostics

Each event should include:

- provider used
- latency
- validation summary
- stale flag
- retry/fallback count
- provider health status

Exit criteria:

- watcher can run a paper scanner loop safely
- rate limits are respected
- stale/invalid data is surfaced explicitly

---

## Phase 7 — Additional Data Coverage

**Goal:** close useful market-data gaps after the data foundation is reliable.

### 7.1 Volume-by-price

- wire KBS matched-by-price endpoint if still available
- return price, buy volume, sell volume, unknown volume, total volume
- add quality and provider contracts before exposing broadly

### 7.2 Historical foreign flow

- investigate daily foreign buy/sell/net flow endpoints
- add time-series support only if source is stable and contract-tested

### 7.3 Level 2 order book normalization

- extract VCI bid/ask ladder from existing price board
- normalize to side/level/price/volume schema
- compare with other providers if available

### 7.4 Open interest history

- investigate futures OI history endpoints
- add only if source is stable enough for contract/live smoke coverage

### 7.5 Index membership history

- investigate sector/index constituent endpoints
- required for correct historical relative-strength and sector rotation studies

---

## Priority Matrix

```text
  High Impact
     │
     │   P1 provider reliability ── next blocker after correctness fixes
     │   P2 rate limit + batch ─── unlocks full-market scans
     │   P3 storage sync ───────── makes research reproducible
     │   P4 scanner readiness ──── clean inputs for pattern detection
     │
     │   P5 ref/fund quality ───── expands trust beyond market data
     │   P6 watcher ────────────── live/paper scanner loop
     │   P7 extra endpoints ────── useful but should wait for foundation
     │
     └────────────────────────────────────────────────────────────
          Lower Effort ───────────────────────────── Higher Effort
```

**Start here:** Phase 1. The correctness gate has largely landed; now make provider reliability operational.

**Biggest unlock after Phase 1:** Phase 2 batch + rate limiting. This enables full-market scans without provider abuse.

**Most important architectural rule:** data quality reports and provider diagnostics must travel with the data. A scanner should never consume anonymous, unvalidated DataFrames.

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
| Foreign flow time-series | unknown | unknown | unknown | no | no | no |
| Volume-by-price | stub/unknown | no | no | no | no | no |
| Level 2 order book | partial | in price_board | unknown | no | no | no |
| Open interest today | yes/futures | unknown | unknown | no | no | no |
| Open interest history | unknown | unknown | unknown | no | no | no |
| Fundamental/company data | yes | yes | no | no | no | yes |
| Forex/crypto OHLCV | no | no | no | yes | yes | no |
| Vietnam sector indices | yes/limited | yes/broad | unknown | no | no | no |
| WebSocket/streaming | no | no | no | no | no | no |

---

## Definition of Done for Scanner-Ready Foundation

The foundation is ready for scanner development only when:

- provider health is integrated into source selection or batch diagnostics
- batch API has structured partial-failure reporting
- rate limiting prevents uncontrolled provider calls
- quality reports attach to every returned dataset or batch item
- provider diagnostics include provider used, latency, fallback count, and stale status
- storage/incremental sync can persist quality and provider diagnostics
- full-market scan results are reproducible and auditable

---

*Last updated: 2026-07-02*
