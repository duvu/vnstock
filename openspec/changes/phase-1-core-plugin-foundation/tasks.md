# Tasks: Phase 1 — Core Contracts and Internal Plugin Foundation

## 1. Dataset contracts

- [ ] Create `vnstock/core/contracts/`.
- [ ] Add `DatasetContract` model.
- [ ] Add `DatasetContractRegistry`.
- [ ] Define `equity.ohlcv` contract.
- [ ] Define `equity.quote` contract.
- [ ] Define `equity.intraday_trades` contract.
- [ ] Define `index.ohlcv` contract.
- [ ] Define `reference.symbols` contract.
- [ ] Define `reference.company_info` contract.
- [ ] Define `fundamental.balance_sheet` contract.
- [ ] Define `fundamental.income_statement` contract.
- [ ] Define `fundamental.cash_flow` contract.
- [ ] Define `fundamental.financial_ratio` contract.
- [ ] Define `fund.nav` contract.
- [ ] Define `foreign_flow.daily` contract.
- [ ] Add tests for contract registration.
- [ ] Add tests for duplicate dataset registration.
- [ ] Add tests for unknown dataset lookup.

## 2. Provider plugin interface

- [ ] Create `vnstock/core/provider/plugin.py`.
- [ ] Define `ProviderPlugin` protocol/interface.
- [ ] Define standard capability metadata shape.
- [ ] Define allowed provider capability status values:
  - `stable`
  - `experimental`
  - `partial`
  - `deprecated`
  - `unsupported`
- [ ] Add tests for provider capability shape.
- [ ] Add a fake provider plugin for tests.

## 3. Provider registry

- [ ] Create `vnstock/core/provider/registry.py`.
- [ ] Implement `register(provider)`.
- [ ] Implement `get(name)`.
- [ ] Implement `providers_for(dataset)`.
- [ ] Implement `names()`.
- [ ] Implement `capability_matrix()`.
- [ ] Ensure provider names are case-insensitive.
- [ ] Add duplicate provider registration error.
- [ ] Add tests for registry lookup.
- [ ] Add tests for dataset candidate lookup.
- [ ] Add tests for capability matrix output.

## 4. Provider router skeleton

- [ ] Create `vnstock/core/provider/router.py`.
- [ ] Implement `ProviderRouter`.
- [ ] Implement explicit source resolution.
- [ ] Implement `source=None` and `source="auto"` behavior.
- [ ] Add default provider priority config hook.
- [ ] Add routing diagnostics object.
- [ ] Add error for unknown provider.
- [ ] Add error for provider that does not support requested dataset.
- [ ] Add tests for explicit source routing.
- [ ] Add tests for auto source routing.
- [ ] Add tests for unsupported dataset routing.
- [ ] Add tests for routing diagnostics.

## 5. DataResult

- [ ] Create `vnstock/core/result.py`.
- [ ] Add `DataResult` dataclass.
- [ ] Add `to_dataframe()` method.
- [ ] Ensure metadata is attached to `DataFrame.attrs`.
- [ ] Ensure no auth secrets are added to metadata.
- [ ] Add tests for metadata propagation.
- [ ] Add tests for empty quality report.
- [ ] Add tests for diagnostics propagation.

## 6. Error model

- [ ] Add base platform exception.
- [ ] Add `DatasetContractError`.
- [ ] Add `ProviderNotFoundError`.
- [ ] Add `UnsupportedDatasetError`.
- [ ] Add `UnsupportedDatasetForProviderError`.
- [ ] Add `ProviderFetchError`.
- [ ] Add tests for expected errors.

## 7. Backward compatibility

- [ ] Confirm current `Market` import remains unchanged.
- [ ] Confirm `Market().equity.ohlcv(...)` remains unchanged.
- [ ] Confirm `validate=True` behavior remains compatible.
- [ ] Confirm `df.attrs["quality"]` remains compatible.
- [ ] Add at least one compatibility test for existing OHLCV call path.
- [ ] Add migration notes for internal maintainers.

## 8. First provider path adaptation

- [ ] Select first provider path for internal plugin routing.
- [ ] Recommended: `equity.ohlcv`.
- [ ] Add internal provider wrapper for selected provider.
- [ ] Route selected path through `ProviderRegistry`.
- [ ] Route selected path through `ProviderRouter`.
- [ ] Return current public `DataFrame`.
- [ ] Preserve provider/quality metadata.
- [ ] Add tests.

## 9. Documentation

- [ ] Add `docs/PLUGIN_ARCHITECTURE.md`.
- [ ] Add `docs/DATASET_CONTRACTS.md`.
- [ ] Add `docs/PROVIDER_PLUGIN_INTERFACE.md`.
- [ ] Add examples for provider capability declaration.
- [ ] Add examples for `DataResult`.
- [ ] Add note that external package split is not part of Phase 1.

## 10. Validation

Run:

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests/unit/core tests/contracts -q
python -m build --sdist --wheel --no-isolation
```

## Completion checklist

Phase 1 is complete when:

- [ ] dataset contract registry exists;
- [ ] provider plugin interface exists;
- [ ] provider registry exists;
- [ ] provider router skeleton exists;
- [ ] `DataResult` exists;
- [ ] at least one provider path is adapted internally;
- [ ] public API remains backward-compatible;
- [ ] unit tests pass;
- [ ] contract tests pass;
- [ ] build passes;
- [ ] docs are updated.
