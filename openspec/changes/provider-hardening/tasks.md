# Tasks: Provider Hardening

## 1. Provider Models

- [ ] Add `vnstock/core/provider/models.py`
- [ ] Implement `ProviderCapability`
- [ ] Implement `ProviderHealth`
- [ ] Implement `ProviderComparisonReport`
- [ ] Implement structured provider issue model
- [ ] Add unit tests for model serialization

## 2. Capability Registry

- [ ] Add `vnstock/core/provider/capabilities.py`
- [ ] Register KBS capabilities
- [ ] Register VCI capabilities
- [ ] Register DNSE capabilities
- [ ] Register MSN capabilities where applicable
- [ ] Register FMP capabilities where applicable
- [ ] Register FMarket capabilities where applicable
- [ ] Add helper to query providers by dataset type, asset class, method, and interval
- [ ] Add tests for unsupported capability behavior

## 3. Contract Fixture Structure

- [ ] Add `tests/fixtures/providers/dnse/`
- [ ] Add `tests/fixtures/providers/kbs/`
- [ ] Add `tests/fixtures/providers/vci/`
- [ ] Add raw sample fixtures for OHLCV daily
- [ ] Add raw sample fixtures for price board
- [ ] Add raw sample fixtures for intraday trades
- [ ] Add normalized expected output fixtures where practical
- [ ] Document fixture update process

## 4. Provider Contract Tests

- [ ] Add `tests/contracts/providers/test_dnse_contracts.py`
- [ ] Add `tests/contracts/providers/test_kbs_contracts.py`
- [ ] Add `tests/contracts/providers/test_vci_contracts.py`
- [ ] Validate raw fixture parsing
- [ ] Validate normalized OHLCV schema
- [ ] Validate normalized price board schema
- [ ] Validate normalized intraday schema
- [ ] Ensure contract tests do not call live endpoints

## 5. Live Smoke Test Infrastructure

- [ ] Add `tests/live/providers/`
- [ ] Add `VNSTOCK_LIVE_TESTS` gating
- [ ] Add `VNSTOCK_LIVE_PROVIDERS` filtering
- [ ] Add `VNSTOCK_LIVE_SYMBOLS` filtering
- [ ] Add pytest markers: `live`, `provider`, `provider_dnse`, `provider_kbs`, `provider_vci`
- [ ] Add skip behavior when live tests are disabled
- [ ] Add documentation for safe live test execution

## 6. Live Smoke Tests

- [ ] Add DNSE live OHLCV smoke test
- [ ] Add DNSE live price board smoke test
- [ ] Add DNSE live intraday smoke test where endpoint supports it
- [ ] Add KBS live OHLCV smoke test
- [ ] Add KBS live price board smoke test
- [ ] Add VCI live OHLCV smoke test
- [ ] Add VCI live price board smoke test
- [ ] Keep all live tests small and rate-limit friendly

## 7. Schema Drift Detection

- [ ] Add `vnstock/core/provider/drift.py`
- [ ] Implement raw schema drift detector
- [ ] Implement normalized schema drift detector
- [ ] Classify drift as `none`, `minor`, or `major`
- [ ] Detect missing required raw fields
- [ ] Detect missing required normalized columns
- [ ] Detect dtype category drift
- [ ] Add unit tests with drift fixtures

## 8. Cross-Provider Comparison

- [ ] Add `vnstock/core/provider/compare.py`
- [ ] Implement OHLCV comparison across KBS, VCI, DNSE
- [ ] Implement missing-date comparison
- [ ] Implement price difference summary
- [ ] Implement volume difference summary
- [ ] Implement price-scale mismatch detection
- [ ] Add configurable tolerances
- [ ] Add tests using synthetic provider outputs

## 9. Provider Health Scoring

- [ ] Add `vnstock/core/provider/health.py`
- [ ] Implement health statuses: `healthy`, `degraded`, `failing`, `unknown`
- [ ] Convert contract test results into health signals
- [ ] Convert live smoke test results into health signals
- [ ] Track latency, error rate, schema status, freshness status, and issues
- [ ] Add tests for health state transitions

## 10. Router Integration

- [ ] Update `vnstock/core/router.py` to optionally use provider health state
- [ ] Prefer healthy providers
- [ ] Allow degraded providers only when necessary
- [ ] Skip failing providers unless caller forces source
- [ ] Add `ignore_provider_health` option
- [ ] Add `include_provider_diagnostics` option
- [ ] Add router tests for health-aware provider selection

## 11. Provider Capability Matrix

- [ ] Add matrix generator utility
- [ ] Generate `docs/PROVIDER_MATRIX.md`
- [ ] Generate machine-readable provider matrix JSON artifact
- [ ] Include provider, dataset type, asset class, method, intervals, auth requirement, contract status, live status, notes
- [ ] Add tests for matrix generation

## 12. CI Integration

- [ ] Add contract tests to normal CI
- [ ] Ensure live tests are skipped in normal CI
- [ ] Add optional scheduled/manual live smoke workflow
- [ ] Add marker docs to `pytest.ini`
- [ ] Fail CI on contract drift
- [ ] Do not fail normal CI on unavailable live providers unless explicitly enabled

## 13. Documentation

- [ ] Add `docs/PROVIDER_HARDENING.md`
- [ ] Document contract tests
- [ ] Document live smoke tests
- [ ] Document provider health statuses
- [ ] Document cross-provider comparison
- [ ] Document provider matrix generation
- [ ] Document how to add a new provider safely

## 14. Rollout Plan

- [ ] Start with DNSE contract fixtures and tests
- [ ] Add KBS and VCI fixtures next
- [ ] Add OHLCV comparison first
- [ ] Add price board comparison second
- [ ] Add intraday comparison last
- [ ] Integrate provider health with router only after contract tests are stable
