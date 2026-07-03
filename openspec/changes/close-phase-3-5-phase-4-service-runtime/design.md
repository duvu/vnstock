# Design: Close Phase 3.5 and Phase 4 Service Runtime

## Overview

This change closes the gap between the implemented plugin platform and the local data service.

Current implementation contains a real `PluginRuntime`, but the local HTTP service still uses a legacy data path for data endpoints. The closure design is to make service endpoints thin wrappers over `PluginRuntime` and serialize `DataResult` as a stable HTTP contract for downstream consumers such as `vnalpha-service`.

## Target service flow

```text
HTTP request
→ canonical endpoint router
→ dataset mapper
→ query parser
→ PluginRuntime.fetch(..., return_result=True)
→ DataResultSerializer
→ JSON response envelope
```

No data endpoint may instantiate legacy `Vnstock` UI objects or provider/explorer classes directly.

## Components

### 1. Dataset mapper

Add a dataset mapper in the service layer.

Suggested module:

```text
vnstock/service/dataset_mapper.py
```

Responsibilities:

- map canonical HTTP paths to dataset names;
- normalize path aliases;
- parse query parameters;
- preserve source/validate/quality_mode parameters;
- reject unknown datasets clearly.

Canonical mapping:

```text
/v1/equity/ohlcv                 → equity.ohlcv
/v1/equity/quote                 → equity.quote
/v1/equity/intraday-trades       → equity.intraday_trades
/v1/index/ohlcv                  → index.ohlcv
/v1/reference/symbols            → reference.symbols
/v1/company/info                 → reference.company_info
/v1/fundamental/balance-sheet    → fundamental.balance_sheet
/v1/fundamental/income-statement → fundamental.income_statement
/v1/fundamental/cash-flow        → fundamental.cash_flow
/v1/fundamental/financial-ratio  → fundamental.financial_ratio
/v1/fund/nav                     → fund.nav
/v1/fund/holdings                → fund.holdings
```

Backward-compatible aliases may be kept temporarily:

```text
/v1/market/ohlcv       → equity.ohlcv
/v1/reference/listing  → reference.symbols
```

Aliases must return the same response envelope and should include a deprecation warning in diagnostics.

### 2. Runtime dependency

The service should initialize one default runtime from:

```python
from vnstock.core.runtime.bootstrap import default_plugin_registry
from vnstock.core.runtime.plugin_runtime import PluginRuntime
```

Suggested module:

```text
vnstock/service/runtime_dependency.py
```

Responsibilities:

- create default plugin registry;
- create `PluginRuntime`;
- allow test injection of fake runtime;
- avoid per-request expensive initialization where practical.

### 3. DataResult serializer

Add a serializer for HTTP responses.

Suggested module:

```text
vnstock/service/serializers.py
```

The serializer should convert `DataResult` into:

```json
{
  "data": [],
  "meta": {
    "request_id": "req_...",
    "dataset": "equity.ohlcv",
    "provider": "KBS",
    "quality_status": "PASS",
    "fetched_at": "2026-07-03T00:00:00Z",
    "source_requested": "auto",
    "runtime_path": "plugin_runtime"
  },
  "diagnostics": {
    "routing": {},
    "provider_diagnostics": {},
    "quality": {},
    "warnings": []
  }
}
```

Required meta fields:

```text
request_id
dataset
provider
quality_status
fetched_at
source_requested
runtime_path
```

Required diagnostics behavior:

- preserve routing diagnostics;
- preserve provider diagnostics after redaction;
- preserve contract/quality diagnostics;
- include alias deprecation warning if applicable;
- never include token/password/api key/cookie/authorization material.

### 4. Provider endpoints

Provider endpoints should use the plugin registry returned by `default_plugin_registry()`.

Endpoints:

```text
GET /v1/providers
GET /v1/providers/capabilities
GET /v1/providers/health
```

Expected behavior:

- `/v1/providers` returns provider names from `PluginRegistry.names()`;
- `/v1/providers/capabilities` returns `PluginRegistry.capability_matrix()`;
- `/v1/providers/health` returns `DEFAULT_HEALTH_STORE` data.

Do not use the legacy `vnstock.core.registry.ProviderRegistry` for these endpoints.

### 5. Auth status

Fix `AuthManager.auth_status_all()` and call sites.

Acceptable options:

1. Change `AuthManager.auth_status_all(providers: list[str] | None = None)` and default to known providers.
2. Keep the strict signature but update all service/CLI call sites to pass provider names.

Preferred option: make the method accept optional providers to preserve ergonomic CLI/service calls.

Auth status response must not include:

```text
token
password
secret
bearer
authorization
cookie
api_key
```

### 6. Forbidden endpoints

The forbidden gate must remain active.

Forbidden endpoints include:

```text
POST /v1/auth/login
POST /v1/auth/tcbs/login
POST /v1/auth/token
GET  /v1/account
GET  /v1/portfolio
POST /v1/order
POST /v1/trade
POST /v1/transfer
POST /v1/margin
POST /v1/portfolio/execute
```

The service may return 404 or 405. It must not implement these handlers.

### 7. Roadmap alignment

Update `roadmap.md` so the REST/API phase does not list REST login/logout endpoints.

Allowed auth endpoints:

```text
GET /v1/auth/status
GET /v1/auth/providers
```

Forbidden auth endpoints:

```text
POST /v1/auth/login
POST /v1/auth/{provider}/login
POST /v1/auth/{provider}/logout
```

### 8. Error mapping

Map runtime errors into stable HTTP errors:

```text
UnsupportedDatasetError     → 404
NoHealthyProviderError      → 503
ProviderFetchError          → 502
DatasetContractError        → 422
ValueError from bad params  → 400
Unknown error               → 500
```

Error payload:

```json
{
  "error": "provider_fetch_error",
  "message": "...",
  "dataset": "equity.ohlcv",
  "request_id": "req_..."
}
```

### 9. Test strategy

Add tests that prove:

- canonical endpoint `/v1/equity/ohlcv` exists;
- data endpoint calls `PluginRuntime.fetch`;
- data response includes `data`, `meta`, `diagnostics`;
- `meta.runtime_path` is `plugin_runtime`;
- provider endpoint uses new plugin registry;
- auth status does not leak secrets;
- forbidden endpoints stay unavailable;
- legacy alias emits deprecation warning if kept.

## Closure decision

After this change:

- Phase 3.5 is closed because service data paths no longer bypass PluginRuntime.
- Phase 4 is closed because local data service/auth/Docker boundaries are coherent and testable.
