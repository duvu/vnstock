# Tasks — Add TCBS Data Provider

## 0. Scope and Safety Gate

- [ ] Confirm TCBS provider is data-only.
- [ ] Confirm no broker login, account, portfolio, margin, order, transfer, or iCopy action endpoint is implemented.
- [ ] Add code comments/docs that TCBS endpoints are unofficial public endpoints and may drift.
- [ ] Add provider-level disclaimer for vendor-derived TCBS fields such as rating, recommendation, valuation, and buy/sell signals.

## 1. Provider Package Skeleton

- [ ] Create `vnstock/explorer/tcbs/__init__.py`.
- [ ] Create `vnstock/explorer/tcbs/const.py`.
- [ ] Create `vnstock/explorer/tcbs/quote.py`.
- [ ] Create `vnstock/explorer/tcbs/trading.py`.
- [ ] Create `vnstock/explorer/tcbs/company.py`.
- [ ] Create `vnstock/explorer/tcbs/fundamental.py`.
- [ ] Create `vnstock/explorer/tcbs/screener.py`.
- [ ] Register TCBS adapters with `ProviderRegistry` where required.

## 2. Endpoint Constants and Field Maps

- [ ] Add base URL: `https://apipubaws.tcbs.com.vn`.
- [ ] Add OHLCV endpoint variants:
  - [ ] `/stock/v2/stock/bars-long-term`
  - [ ] `/stock-insight/v2/stock/bars-long-term`
  - [ ] `/stock-insight/v1/stock/bars-long-term`
- [ ] Add intraday endpoint candidate: `/stock/v1/intraday/{symbol}/his/paging`.
- [ ] Add price board endpoint: `/stock/v1/stock/second-tc-price`.
- [ ] Add company/reference endpoints.
- [ ] Add financial endpoints.
- [ ] Add screener endpoint: `/ligo/v1/watchlist/preview`.
- [ ] Add interval map: `1m`, `5m`, `15m`, `30m`, `1H`, `1D`, `1W`, `1M`.
- [ ] Add OHLCV raw-to-normalized map.
- [ ] Add price board raw-to-normalized map.
- [ ] Add screener raw-to-normalized map.

## 3. Quote Adapter

- [ ] Implement `Quote.history()` for TCBS OHLCV.
- [ ] Support `symbol`, `start`, `end`, `interval`, `count_back`, `length`, `to_df`, `get_all` where compatible.
- [ ] Implement endpoint fallback order.
- [ ] Record successful endpoint variant in `df.attrs["endpoint_variant"]`.
- [ ] Normalize OHLCV columns to `time/open/high/low/close/volume`.
- [ ] Normalize timestamp to timezone-naive Vietnam local time where needed.
- [ ] Attach metadata attrs: source, symbol, interval, start, end, fetched_at.
- [ ] Add input validation for symbol, date range, interval, and asset type.
- [ ] Add structured errors for missing data, malformed response, unsupported interval, and endpoint fallback exhaustion.
- [ ] Implement `Quote.intraday()` only if public live smoke verifies endpoint reliability.
- [ ] If intraday remains uncertain, declare it experimental or unavailable.

## 4. Trading / Price Board Adapter

- [ ] Implement `Trading.price_board(symbols_list, show_log=False, get_all=False)`.
- [ ] Validate non-empty `symbols_list`.
- [ ] Call `second-tc-price` with comma-separated tickers.
- [ ] Normalize minimum required fields: symbol, close_price, volume_accumulated where present.
- [ ] Normalize extended fields for technical, valuation, relative-strength, foreign, and market-score data.
- [ ] Prefix or document vendor-derived columns clearly.
- [ ] Attach metadata attrs: source, symbols, get_all, fetched_at.
- [ ] Support `validate=True` and `quality_mode` integration through the UI dispatch path.

## 5. Company Adapter

- [ ] Implement `Company.info()` or equivalent overview method using `/tcanalysis/v1/ticker/{symbol}/overview`.
- [ ] Implement `Company.profile()` using `/tcanalysis/v1/company/{symbol}/overview` if response is distinct and useful.
- [ ] Implement `Company.shareholders()` using large-shareholders endpoint.
- [ ] Implement `Company.insider_trading()` using insider-dealing endpoint.
- [ ] Implement `Company.subsidiaries()`.
- [ ] Implement `Company.officers()`.
- [ ] Implement `Company.events()`.
- [ ] Implement `Company.news()`.
- [ ] Implement `Company.dividends()`.
- [ ] Normalize pagination metadata.
- [ ] Preserve raw fields when `get_all=True`.

## 6. Symbol Industry Adapter

- [ ] Implement symbol industry extraction from TCBS company overview.
- [ ] Normalize as classification system `TCBS_INTERNAL`.
- [ ] Output columns:
  - [ ] symbol
  - [ ] provider
  - [ ] classification_system
  - [ ] industry_code
  - [ ] industry_name
  - [ ] fetched_at
- [ ] Do not map TCBS_INTERNAL to ICB unless a verified mapping exists.
- [ ] Add support through `Reference.equity.list_by_industry(source="TCBS")` if compatible.

## 7. Fundamental Adapter

- [ ] Implement balance sheet endpoint.
- [ ] Implement income statement endpoint.
- [ ] Implement cash flow endpoint.
- [ ] Implement financial ratios endpoint.
- [ ] Support `period="year"` and `period="quarter"`.
- [ ] Map period to TCBS query parameters `yearly=true|false`.
- [ ] Preserve raw TCBS line items initially.
- [ ] Normalize common metadata: symbol, year, quarter, period_type, report_type, provider, fetched_at.
- [ ] Add structured errors for unsupported period and malformed responses.

## 8. Screener Adapter

- [ ] Implement `Screener.stock(params, limit=50, id=None, lang="vi", get_all=False)`.
- [ ] Build `filters` payload from params.
- [ ] Parse `searchData.pageContent`.
- [ ] Normalize stable screener fields.
- [ ] Extract multilingual values for known fields when `lang` is provided.
- [ ] Preserve raw fields when `get_all=True`.
- [ ] Mark screener API as experimental in docs and provider capabilities.
- [ ] Do not expose screener output as investment advice.

## 9. Provider Capability Registry

- [ ] Add TCBS OHLCV equity capability.
- [ ] Add TCBS price board equity capability.
- [ ] Add TCBS company profile capability.
- [ ] Add TCBS symbol industry capability with `classification_system=TCBS_INTERNAL` in notes.
- [ ] Add TCBS financial statement and ratio capabilities.
- [ ] Add TCBS vendor screener capability marked experimental.
- [ ] Add intraday capability only after live smoke confirms public availability.

## 10. Unified UI / API Integration

- [ ] Add TCBS support to API adapter source validation where applicable.
- [ ] Add `source="TCBS"` for `Market.equity.ohlcv`.
- [ ] Add `source="TCBS"` for `Market.equity.quote`.
- [ ] Add `source="TCBS"` for `Reference.company.info` where compatible.
- [ ] Add `source="TCBS"` for `Reference.equity.list_by_industry` where compatible.
- [ ] Add `source="TCBS"` for fundamental statement methods where compatible.
- [ ] Do not make TCBS the default provider in this change.

## 11. Fixtures and Contract Tests

- [ ] Add raw fixture: `tests/fixtures/providers/tcbs/ohlcv_daily_raw.json`.
- [ ] Add normalized fixture or expected schema for OHLCV.
- [ ] Add raw fixture for price board.
- [ ] Add raw fixture for company overview.
- [ ] Add raw fixture for financial ratios.
- [ ] Add raw fixture for screener.
- [ ] Add `tests/contracts/providers/test_tcbs_contracts.py`.
- [ ] Test OHLCV parser against fixture.
- [ ] Test price board parser against fixture.
- [ ] Test company overview parser against fixture.
- [ ] Test symbol industry normalization.
- [ ] Test financial ratio parser.
- [ ] Test screener parser.
- [ ] Test malformed response handling.
- [ ] Confirm contract tests do not call network.

## 12. Live Smoke Tests

- [ ] Add `tests/live/providers/test_tcbs_live.py`.
- [ ] Mark tests with `live`, `provider`, and `provider_tcbs`.
- [ ] Ensure live tests skip unless `VNSTOCK_LIVE_TESTS=true`.
- [ ] Support `VNSTOCK_LIVE_PROVIDERS=TCBS`.
- [ ] Test OHLCV daily for one symbol and short range.
- [ ] Test price board for one to three symbols.
- [ ] Test company overview for one symbol.
- [ ] Test financial ratios for one symbol.
- [ ] Test screener minimal payload.
- [ ] Test intraday only if stable and public.
- [ ] Keep live smoke request count small.

## 13. Data Quality Integration

- [ ] Ensure TCBS OHLCV output can pass existing OHLCV quality validator.
- [ ] Ensure TCBS price board output can pass existing price board quality validator or document missing optional fields.
- [ ] Attach `df.attrs["quality"]` when validation is enabled.
- [ ] Add quality regression tests for TCBS normalized samples.

## 14. Provider Hardening Integration

- [ ] Add TCBS drift baselines for raw and normalized schemas.
- [ ] Add TCBS to provider matrix generation.
- [ ] Add TCBS health scoring test cases.
- [ ] Add TCBS to cross-provider OHLCV comparison if schema is compatible.
- [ ] Keep TCBS health `unknown` or `degraded` until live smoke passes.

## 15. Documentation

- [ ] Update `README.md` provider table.
- [ ] Update `docs/PROVIDER_HARDENING.md`.
- [ ] Update `docs/DATA_QUALITY.md` if TCBS-specific caveats are needed.
- [ ] Update `roadmap.md` to move TCBS from discovery candidate to implementation candidate.
- [ ] Document unofficial public endpoint risk.
- [ ] Document vendor-derived screener/rating fields.

## 16. Validation Commands

Run before implementation PR is ready:

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests/unit/core/quality tests/unit/core/provider tests/contracts/providers -q
PYTHONPATH=. pytest -m "not slow" tests/unit/core tests/unit/ui tests/unified_ui tests/contracts
python -m build --sdist --wheel --no-isolation
```

Optional live smoke:

```bash
VNSTOCK_LIVE_TESTS=true VNSTOCK_LIVE_PROVIDERS=TCBS VNSTOCK_LIVE_SYMBOLS=FPT pytest tests/live/providers/test_tcbs_live.py -m live -v
```

## 17. Exit Criteria

- [ ] TCBS adapters implement only data-only endpoints.
- [ ] OHLCV, price board, company overview, symbol industry, financial ratios, and screener have fixtures.
- [ ] Contract tests pass offline.
- [ ] Live smoke tests are opt-in and documented.
- [ ] Provider capabilities are declared.
- [ ] Quality validation works for TCBS OHLCV and price board.
- [ ] TCBS is not the default provider.
- [ ] Screener remains experimental until field stability is proven.
