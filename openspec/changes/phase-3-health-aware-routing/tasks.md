# Tasks: Phase 3 — Health-aware Routing and Provider Diagnostics

## 0. Prerequisite check

- [ ] Confirm Phase 1 `DatasetContract` exists.
- [ ] Confirm Phase 1 `ProviderPlugin` exists.
- [ ] Confirm Phase 1 `ProviderRegistry` exists.
- [ ] Confirm Phase 1 `ProviderRouter` exists.
- [ ] Confirm Phase 1 `DataResult` exists.
- [ ] Confirm Phase 2 provider plugins exist.
- [ ] Confirm Phase 2 provider capabilities exist.
- [ ] Confirm Phase 2 provider limitations metadata exists.

## 1. Provider health model

- [ ] Create `vnstock/core/provider/health.py`.
- [ ] Add `ProviderHealth`.
- [ ] Define health statuses:
  - `HEALTHY`
  - `DEGRADED`
  - `FAILING`
  - `UNKNOWN`
  - `DISABLED`
- [ ] Add status semantics docs.
- [ ] Add unit tests for health model construction.
- [ ] Add unit tests for health status validation.

## 2. Provider health store

- [ ] Add `ProviderHealthStore` interface.
- [ ] Add `InMemoryProviderHealthStore`.
- [ ] Implement `get(provider, dataset)`.
- [ ] Implement `set(health)`.
- [ ] Implement `record_success(...)`.
- [ ] Implement `record_failure(...)`.
- [ ] Implement `list_for_dataset(dataset)`.
- [ ] Add tests for missing health defaulting to `UNKNOWN`.
- [ ] Add tests for success updates.
- [ ] Add tests for failure updates.

## 3. Provider cooldown

- [ ] Add cooldown model.
- [ ] Add cooldown calculation helper.
- [ ] Add active cooldown check.
- [ ] Add cooldown on repeated failures.
- [ ] Add cooldown diagnostics.
- [ ] Add tests for short cooldown.
- [ ] Add tests for repeated failure cooldown.
- [ ] Add tests for cooldown expiry.
- [ ] Add tests that active cooldown provider is skipped in auto routing.

## 4. Routing policy

- [ ] Add `RoutingPolicy`.
- [ ] Add default routing policy.
- [ ] Support `prefer_healthy`.
- [ ] Support `allow_degraded`.
- [ ] Support `allow_failing_fallback`.
- [ ] Support `respect_cooldown`.
- [ ] Support `use_priority_tiebreaker`.
- [ ] Add tests for policy behavior.

## 5. Routing decision and diagnostics

- [ ] Add `RoutingDecision`.
- [ ] Add routing diagnostics serializer.
- [ ] Include dataset.
- [ ] Include requested source.
- [ ] Include selected provider.
- [ ] Include candidate providers.
- [ ] Include rejected providers.
- [ ] Include fallback flag.
- [ ] Include routing reason.
- [ ] Include health snapshot.
- [ ] Include warnings.
- [ ] Add tests for diagnostics completeness.
- [ ] Add tests that diagnostics do not contain sensitive credential material.

## 6. ProviderRouter health-aware behavior

- [ ] Update `ProviderRouter` to accept health store.
- [ ] Update `ProviderRouter` to accept routing policy.
- [ ] Implement auto routing by health.
- [ ] Implement provider priority tie-breaker.
- [ ] Implement active cooldown rejection.
- [ ] Implement degraded fallback behavior.
- [ ] Ensure failing providers are rejected by default.
- [ ] Add option to allow failing fallback through policy.
- [ ] Add explicit source behavior with health warning.
- [ ] Add tests for healthy provider selection.
- [ ] Add tests for degraded fallback.
- [ ] Add tests for failing provider rejection.
- [ ] Add tests for explicit source degraded warning.
- [ ] Add tests for unsupported explicit source.

## 7. Success/failure recording

- [ ] Wrap provider fetch with success/failure recording.
- [ ] Record latency where available.
- [ ] Record freshness score where available.
- [ ] Record fetch failure.
- [ ] Record validation failure.
- [ ] Reset or decay failure count on success.
- [ ] Add tests for success after failure.
- [ ] Add tests for validation failure marking provider degraded or failing.

## 8. DataResult diagnostics integration

- [ ] Attach routing diagnostics to `DataResult.diagnostics`.
- [ ] Attach provider diagnostics to `DataResult.diagnostics`.
- [ ] Attach selected provider to `DataResult.provider`.
- [ ] Preserve existing `DataFrame.attrs`.
- [ ] Add tests for DataFrame attrs diagnostics.
- [ ] Add tests for backward compatibility of `df.attrs.get("quality")`.

## 9. Provider comparison expansion

- [ ] Create or update `vnstock/core/provider/comparison.py`.
- [ ] Harden `compare_ohlcv`.
- [ ] Add `compare_quote`.
- [ ] Add `compare_intraday_shape`.
- [ ] Add `compare_coverage`.
- [ ] Add `compare_freshness`.
- [ ] Add provider-specific tolerance hooks.
- [ ] Add tests for OHLCV comparison.
- [ ] Add tests for quote comparison.
- [ ] Add tests for intraday shape comparison.
- [ ] Add tests for freshness comparison.
- [ ] Add tests for missing columns before comparison access.

## 10. Error model

- [ ] Add `NoProviderForDatasetError`.
- [ ] Add `NoHealthyProviderError`.
- [ ] Add `ProviderInCooldownError`.
- [ ] Add `ProviderDisabledError`.
- [ ] Ensure auto routing errors include candidate/rejection context.
- [ ] Add tests for error messages.

## 11. Configuration

- [ ] Add default provider priority by dataset.
- [ ] Use priority as tie-breaker.
- [ ] Add tests for priority ordering.
- [ ] Document future YAML/env config option.
- [ ] Avoid introducing auth policies in Phase 3.

## 12. Documentation

- [ ] Add `docs/PROVIDER_ROUTING.md`.
- [ ] Add `docs/PROVIDER_DIAGNOSTICS.md`.
- [ ] Document health statuses.
- [ ] Document routing policy.
- [ ] Document explicit source behavior.
- [ ] Document auto source behavior.
- [ ] Document cooldown behavior.
- [ ] Document comparison APIs.
- [ ] Document diagnostics examples.
- [ ] Document data-only boundary.

## 13. Backward compatibility

- [ ] Confirm `Market().equity.ohlcv(...)` remains compatible.
- [ ] Confirm explicit `source=` remains compatible.
- [ ] Confirm `source="auto"` remains compatible.
- [ ] Confirm `validate=True` quality metadata remains compatible.
- [ ] Confirm public return type remains `pandas.DataFrame`.

## 14. Validation

Run:

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests/unit/core tests/contracts -q
python -m build --sdist --wheel --no-isolation
```

## Completion checklist

Phase 3 is complete when:

- [ ] provider health model exists;
- [ ] provider health store exists;
- [ ] cooldown behavior exists;
- [ ] routing policy exists;
- [ ] routing decision/diagnostics exist;
- [ ] router selects providers by health;
- [ ] explicit source behavior is preserved;
- [ ] diagnostics attach to result metadata;
- [ ] comparison APIs are expanded;
- [ ] unit tests pass;
- [ ] contract tests pass;
- [ ] public API remains backward-compatible;
- [ ] data-only boundary remains enforced;
- [ ] docs are updated.
