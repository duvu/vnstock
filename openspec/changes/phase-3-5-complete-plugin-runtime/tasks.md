# Tasks: Phase 3.5 — Complete Plugin Runtime and Retire Legacy Dispatch

## 0. Prerequisite check

- [ ] Confirm Phase 1 `DatasetContract` exists.
- [ ] Confirm Phase 1 `ProviderPlugin` exists.
- [ ] Confirm Phase 1 `PluginRegistry` exists.
- [ ] Confirm Phase 1 `PluginRouter` exists.
- [ ] Confirm Phase 1 `DataResult` exists.
- [ ] Confirm Phase 2 provider plugins exist.
- [ ] Confirm Phase 3 health-aware routing exists.
- [ ] Confirm current public API paths that still bypass plugin runtime.
- [ ] List all public methods that need migration.

## 1. Runtime package

- [ ] Create `vnstock/core/runtime/`.
- [ ] Add `vnstock/core/runtime/__init__.py`.
- [ ] Add `vnstock/core/runtime/plugin_runtime.py`.
- [ ] Add `vnstock/core/runtime/bootstrap.py`.
- [ ] Add `vnstock/core/runtime/request.py`.
- [ ] Add unit tests for runtime initialization.

## 2. DatasetRequest

- [ ] Add `DatasetRequest` dataclass.
- [ ] Include dataset name.
- [ ] Include params.
- [ ] Include source.
- [ ] Include validate flag.
- [ ] Include return_result flag.
- [ ] Add tests for request construction.
- [ ] Add tests for invalid dataset request.

## 3. Provider bootstrap

- [ ] Add `default_plugin_registry()`.
- [ ] Register KBS plugin.
- [ ] Register VCI plugin.
- [ ] Register DNSE plugin.
- [ ] Register TCBS plugin.
- [ ] Register FMarket plugin.
- [ ] Register MSN plugin.
- [ ] Register FMP plugin.
- [ ] Add tests for default registry provider names.
- [ ] Add tests for default registry capability matrix.

## 4. PluginRuntime core

- [ ] Implement `PluginRuntime`.
- [ ] Accept DatasetContractRegistry.
- [ ] Accept PluginRegistry.
- [ ] Accept PluginRouter.
- [ ] Accept provider health store.
- [ ] Implement `fetch(dataset, params, source, validate, return_result)`.
- [ ] Resolve dataset contract.
- [ ] Resolve provider through PluginRouter.
- [ ] Call provider parameter validation.
- [ ] Call provider fetch.
- [ ] Wrap output in DataResult.
- [ ] Attach routing diagnostics.
- [ ] Attach provider diagnostics.
- [ ] Attach runtime path diagnostics.
- [ ] Return DataFrame by default.
- [ ] Return DataResult when requested.

## 5. Health update integration

- [ ] Record success after successful provider fetch and validation.
- [ ] Record failure after provider fetch error.
- [ ] Record failure after contract validation error.
- [ ] Preserve routing diagnostics after failure where practical.
- [ ] Add tests for success recording.
- [ ] Add tests for failure recording.
- [ ] Add tests for cooldown effect through runtime.

## 6. Contract validation integration

- [ ] Validate output against DatasetContract when `validate=True`.
- [ ] Support lightweight contract validation even when quality validation is disabled.
- [ ] Ensure missing required columns fail clearly.
- [ ] Ensure required metadata is attached.
- [ ] Add tests for valid output.
- [ ] Add tests for missing required columns.
- [ ] Add tests for optional columns.

## 7. Public API migration — Market

- [ ] Identify current `Market` implementation path.
- [ ] Map `Market().equity.ohlcv(...)` to `equity.ohlcv`.
- [ ] Map quote/price board methods to `equity.quote`.
- [ ] Map intraday methods to `equity.intraday_trades`.
- [ ] Route migrated methods through PluginRuntime.
- [ ] Preserve public method signatures.
- [ ] Preserve public DataFrame return type.
- [ ] Add compatibility tests.
- [ ] Add tests that migrated methods do not use legacy dispatch.

## 8. Public API migration — Reference

- [ ] Identify current `Reference` implementation path.
- [ ] Map symbol list to `reference.symbols`.
- [ ] Map company info to `reference.company_info`.
- [ ] Route migrated methods through PluginRuntime.
- [ ] Add compatibility tests.
- [ ] Add tests that migrated methods do not use legacy dispatch.

## 9. Public API migration — Fundamental

- [ ] Identify current `Fundamental` implementation path.
- [ ] Map balance sheet to `fundamental.balance_sheet`.
- [ ] Map income statement to `fundamental.income_statement`.
- [ ] Map cash flow to `fundamental.cash_flow`.
- [ ] Map financial ratio to `fundamental.financial_ratio`.
- [ ] Route migrated methods through PluginRuntime.
- [ ] Add compatibility tests.
- [ ] Add tests that migrated methods do not use legacy dispatch.

## 10. Public API migration — Retail/Fund

- [ ] Identify current `Retail` implementation path.
- [ ] Map fund NAV to `fund.nav`.
- [ ] Route migrated methods through PluginRuntime.
- [ ] Add compatibility tests.
- [ ] Add tests that migrated methods do not use legacy dispatch.

## 11. Legacy fallback control

- [ ] Add `allow_legacy_fallback` setting.
- [ ] Default fallback to disabled for migrated datasets.
- [ ] Emit diagnostics when fallback is used.
- [ ] Add tests for fallback disabled.
- [ ] Add tests for fallback explicit opt-in.
- [ ] Add tests that migrated datasets never silently fallback.

## 12. Remove or quarantine legacy dispatch

- [ ] Identify legacy dispatch modules.
- [ ] Remove direct public calls for migrated datasets.
- [ ] Rename internal-only legacy helpers where needed.
- [ ] Add deprecation notes for legacy imports.
- [ ] Add tests that public APIs use PluginRuntime.
- [ ] Keep low-level provider client code only behind provider plugins.

## 13. DataResult and diagnostics

- [ ] Ensure every runtime fetch creates DataResult.
- [ ] Attach `dataset`.
- [ ] Attach `provider`.
- [ ] Attach `quality_status`.
- [ ] Attach `quality`.
- [ ] Attach `diagnostics`.
- [ ] Attach `fetched_at`.
- [ ] Attach `runtime_path`.
- [ ] Add tests for DataFrame attrs.
- [ ] Add tests for diagnostics completeness.
- [ ] Add tests that diagnostics contain no credential material.

## 14. Comparison tests

- [ ] Add plugin-vs-legacy comparison tests for migrated datasets before removing fallback.
- [ ] Define acceptable differences.
- [ ] Document schema normalization differences.
- [ ] Remove comparison dependency once legacy path is retired.

## 15. Documentation

- [ ] Add `docs/PLUGIN_RUNTIME_MIGRATION.md`.
- [ ] Document plugin runtime architecture.
- [ ] Document public API migration.
- [ ] Document fallback policy.
- [ ] Document how provider plugins wrap old clients.
- [ ] Document Phase 4 dependency on PluginRuntime.
- [ ] Document data-only boundary.

## 16. Validation

Run:

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests/unit/core tests/integration/plugin_runtime tests/contracts -q
python -m build --sdist --wheel --no-isolation
```

## Completion checklist

Phase 3.5 is complete when:

- [ ] PluginRuntime exists;
- [ ] default provider registry bootstrap exists;
- [ ] public supported datasets route through PluginRuntime;
- [ ] migrated datasets do not silently use legacy dispatch;
- [ ] legacy clients are only used behind provider plugins;
- [ ] DataResult metadata is consistently attached;
- [ ] routing diagnostics are visible in `DataFrame.attrs`;
- [ ] health update works through runtime;
- [ ] compatibility tests pass;
- [ ] legacy fallback is disabled by default for migrated datasets;
- [ ] Phase 4 can build service endpoints on PluginRuntime only.
