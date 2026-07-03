# Change Proposal: Close Phase 3.5 and Phase 4 Service Runtime

## Change ID

`close-phase-3-5-phase-4-service-runtime`

## Summary

Close the remaining gaps in Phase 3.5 PluginRuntime completion and Phase 4 Auth-aware Local Data Service.

The current codebase already contains `PluginRuntime`, provider plugin bootstrap, auth core, CLI auth, CLI serve, a local HTTP service, Dockerfile, docker-compose, and service boundary tests. However, the service data path still bypasses `PluginRuntime` and uses legacy `Vnstock` dispatch for data endpoints.

This change makes the local data service service-ready by requiring every supported data endpoint to route through `PluginRuntime`, serialize `DataResult` into a stable HTTP response envelope, expose canonical v1 data endpoints, and remove remaining legacy registry/API mismatches.

## Problem

The audit found these blockers:

1. `vnstock/service/server.py` handles data requests through legacy `Vnstock` calls instead of `PluginRuntime`.
2. Service endpoints use `/v1/market/ohlcv` style paths, while the target contract expects `/v1/equity/ohlcv`, `/v1/index/ohlcv`, `/v1/reference/symbols`, and related canonical paths.
3. Data responses return only `{data, dataset}` and do not expose `meta` and `diagnostics` from `DataResult`.
4. Provider endpoints use the older `vnstock.core.registry.ProviderRegistry` shape instead of the new plugin registry returned by `default_plugin_registry()`.
5. `AuthManager.auth_status_all()` signature and call sites are inconsistent.
6. The old roadmap still contains REST login endpoints, which now conflict with the local command-based auth design.

## Goals

### G1. Service endpoints use PluginRuntime

All supported data endpoints MUST call `PluginRuntime.fetch(..., return_result=True)`.

### G2. Canonical HTTP API paths

Add canonical read-only data endpoints:

```text
GET /v1/equity/ohlcv
GET /v1/equity/quote
GET /v1/equity/intraday-trades
GET /v1/index/ohlcv
GET /v1/reference/symbols
GET /v1/company/info
GET /v1/fundamental/balance-sheet
GET /v1/fundamental/income-statement
GET /v1/fundamental/cash-flow
GET /v1/fundamental/financial-ratio
GET /v1/fund/nav
GET /v1/fund/holdings
```

### G3. Stable DataResult response envelope

All data endpoints MUST serialize `DataResult` into:

```text
data
meta
diagnostics
```

### G4. Provider endpoints use plugin registry

Provider and capability endpoints MUST use the new plugin registry/bootstrap, not the older provider-type/source registry.

### G5. Auth status is safe and functional

Auth status endpoints and CLI status MUST not expose secrets and MUST not break due to signature mismatch.

### G6. Preserve forbidden endpoint boundary

The service MUST NOT expose REST login, order, account, portfolio, transfer, margin, or trading endpoints.

### G7. Update roadmap alignment

The roadmap MUST not contain REST login endpoints as an approved target for `vnstock-service`.

## Non-goals

This change does not implement:

- FastAPI migration;
- OpenAPI schema generation;
- rate limiter;
- retry policy;
- batch ingestion;
- archive/storage sinks;
- MCP server;
- TUI data console;
- new provider implementations;
- trading signals;
- stock recommendations;
- broker/account/order/portfolio APIs.

## Success criteria

Phase 3.5 can be closed when:

- supported service data endpoints call `PluginRuntime`;
- migrated datasets do not silently use legacy dispatch;
- service responses include `runtime_path = plugin_runtime` in diagnostics;
- tests fail if data endpoints bypass runtime.

Phase 4 can be closed when:

- `vnstock-serve` starts the local service;
- canonical read-only v1 data endpoints return stable envelopes;
- provider endpoints return plugin capability and health data;
- auth status endpoints work without exposing credential material;
- forbidden endpoints return 404 or 405;
- Docker/local-only deployment remains supported.

## Validation commands

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests/unit/core/runtime tests/unit/service tests/contracts -q
python -m build --sdist --wheel --no-isolation
```
