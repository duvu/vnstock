# Tasks: Phase 2 — Normalize Existing Providers as Internal Plugins

## 0. Prerequisite check

- [ ] Confirm Phase 1 `DatasetContract` exists.
- [ ] Confirm Phase 1 `ProviderPlugin` exists.
- [ ] Confirm Phase 1 `ProviderRegistry` exists.
- [ ] Confirm Phase 1 `ProviderRouter` exists.
- [ ] Confirm Phase 1 `DataResult` exists.
- [ ] Confirm at least one provider path is already routed through the internal platform boundary.

## 1. Provider module layout

- [ ] Create or normalize `vnstock/providers/kbs/`.
- [ ] Create or normalize `vnstock/providers/vci/`.
- [ ] Create or normalize `vnstock/providers/dnse/`.
- [ ] Create or normalize `vnstock/providers/tcbs/`.
- [ ] Create or normalize `vnstock/providers/fmarket/`.
- [ ] Create or normalize `vnstock/providers/msn/`.
- [ ] Create or normalize `vnstock/providers/fmp/`.
- [ ] Add `plugin.py` for each provider.
- [ ] Add `capabilities.py` for each provider.
- [ ] Add `normalize.py` for each provider where needed.
- [ ] Preserve existing provider client code where possible.

## 2. Provider capability declarations

- [ ] Define capability shape used by all providers.
- [ ] Add KBS capability declaration.
- [ ] Add VCI capability declaration.
- [ ] Add DNSE capability declaration.
- [ ] Add TCBS capability declaration.
- [ ] Add FMarket capability declaration.
- [ ] Add MSN capability declaration.
- [ ] Add FMP capability declaration.
- [ ] Include `supported` flag per dataset.
- [ ] Include `status` per dataset.
- [ ] Include `auth_required` per dataset.
- [ ] Include supported intervals where applicable.
- [ ] Include provider notes where applicable.

## 3. Provider limitations metadata

- [ ] Add limitations metadata model or convention.
- [ ] Add KBS limitations metadata.
- [ ] Add VCI limitations metadata.
- [ ] Add DNSE limitations metadata.
- [ ] Add TCBS limitations metadata.
- [ ] Add FMarket limitations metadata.
- [ ] Add MSN limitations metadata.
- [ ] Add FMP limitations metadata.
- [ ] Explicitly mark broker/account/order capabilities as out of scope.

## 4. Dataset handler mapping

- [ ] Add dataset-to-method mapping in each provider plugin.
- [ ] Map `equity.ohlcv` where supported.
- [ ] Map `equity.quote` where supported.
- [ ] Map `equity.intraday_trades` where supported.
- [ ] Map `index.ohlcv` where supported.
- [ ] Map `reference.company_info` where supported.
- [ ] Map `fundamental.balance_sheet` where supported.
- [ ] Map `fund.nav` where supported.
- [ ] Ensure unsupported datasets raise `UnsupportedDatasetForProviderError`.

## 5. Normalizers

- [ ] Add or normalize `normalize_equity_ohlcv()` per provider where needed.
- [ ] Add or normalize `normalize_equity_quote()` per provider where needed.
- [ ] Add or normalize `normalize_intraday_trades()` per provider where needed.
- [ ] Add or normalize `normalize_company_info()` per provider where needed.
- [ ] Add or normalize `normalize_balance_sheet()` per provider where needed.
- [ ] Ensure normalizers output required dataset contract columns.
- [ ] Ensure normalizers fail clearly on missing required columns.
- [ ] Ensure normalizers preserve useful provider metadata safely.

## 6. Provider registry integration

- [ ] Register KBS provider plugin.
- [ ] Register VCI provider plugin.
- [ ] Register DNSE provider plugin.
- [ ] Register TCBS provider plugin.
- [ ] Register FMarket provider plugin.
- [ ] Register MSN provider plugin.
- [ ] Register FMP provider plugin.
- [ ] Ensure provider names are case-insensitive.
- [ ] Ensure duplicate registration fails.
- [ ] Ensure `providers_for(dataset)` returns correct candidates.

## 7. First adapted dataset path

- [ ] Adapt `equity.ohlcv` across core Vietnamese equity providers.
- [ ] Confirm public `Market().equity.ohlcv(...)` remains compatible.
- [ ] Confirm `source="KBS"` works where supported.
- [ ] Confirm `source="VCI"` works where supported.
- [ ] Confirm `source="DNSE"` works where supported.
- [ ] Confirm `source="TCBS"` works where supported.
- [ ] Confirm `source="auto"` uses Phase 1 router behavior.
- [ ] Confirm `validate=True` still attaches quality metadata.

## 8. Fixtures

- [ ] Add KBS fixtures for `equity.ohlcv`.
- [ ] Add VCI fixtures for `equity.ohlcv`.
- [ ] Add DNSE fixtures for `equity.ohlcv`.
- [ ] Add TCBS fixtures for `equity.ohlcv`.
- [ ] Add quote fixtures where supported.
- [ ] Add intraday fixtures where supported.
- [ ] Add valid response fixture.
- [ ] Add empty but valid response fixture.
- [ ] Add invalid symbol fixture.
- [ ] Add missing optional fields fixture.
- [ ] Add unexpected extra fields fixture.
- [ ] Add schema drift sample fixture.

## 9. Contract tests

- [ ] Add provider contract test helper.
- [ ] Add KBS provider contract tests.
- [ ] Add VCI provider contract tests.
- [ ] Add DNSE provider contract tests.
- [ ] Add TCBS provider contract tests.
- [ ] Add FMarket provider contract tests where supported.
- [ ] Add MSN/FMP provider contract tests where supported.
- [ ] Test capability declarations.
- [ ] Test unsupported dataset behavior.
- [ ] Test fixture normalization.
- [ ] Test required columns after normalization.
- [ ] Test limitations metadata.
- [ ] Test data-only capability boundary.

## 10. Capability matrix

- [ ] Implement provider capability matrix output from registry.
- [ ] Include provider name.
- [ ] Include dataset name.
- [ ] Include supported status.
- [ ] Include capability status.
- [ ] Include auth requirement.
- [ ] Include intervals where applicable.
- [ ] Add deterministic tests for matrix output.

## 11. Documentation

- [ ] Add `docs/PROVIDER_PLUGIN_NORMALIZATION.md`.
- [ ] Document provider module layout.
- [ ] Document capability declaration format.
- [ ] Document limitations metadata format.
- [ ] Document fixture expectations.
- [ ] Document contract test expectations.
- [ ] Document migration strategy for current providers.
- [ ] Document that external provider packages are deferred.

## 12. Validation

Run:

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests/unit/core tests/contracts -q
python -m build --sdist --wheel --no-isolation
```

## Completion checklist

Phase 2 is complete when:

- [ ] existing core providers have internal plugin wrappers;
- [ ] capabilities are declared for each provider;
- [ ] limitations are declared for each provider;
- [ ] dataset-to-method mapping exists;
- [ ] provider outputs normalize to dataset contracts;
- [ ] fixtures exist for core provider datasets;
- [ ] provider contract tests pass;
- [ ] capability matrix is generated from registry;
- [ ] public API remains backward-compatible;
- [ ] data-only boundary remains enforced;
- [ ] docs are updated.
