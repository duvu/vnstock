# Project Overview
- `vnstock` is a Python package for Vietnamese market/financial data extraction and analysis.
- Requires Python `>=3.10`; package metadata and dependencies are in `pyproject.toml`.
- Public entrypoint is `vnstock/__init__.py`, exporting legacy API classes (`Quote`, `Listing`, `Company`, `Finance`, `Trading`, `Vnstock`) plus v4 Unified UI (`Reference`, `Market`, `Fundamental`, `Retail`, `Broker`, `show_api`, `show_doc`).
- Main code layout: `vnstock/ui` for Unified UI facade/routing/auto-docs, `vnstock/api` for legacy adapters, `vnstock/explorer` for scraping/public web providers (`kbs`, `vci`, `msn`, `fmarket`, `misc`), `vnstock/connector` for API/broker connectors (`fmp`, `dnse`), `vnstock/core` for shared registry/types/utils, `tests` for pytest suites.
- Flat access model: do not add package-level user registration, tier gates, entitlement checks, or private-package fallback routing. Keep external provider credentials scoped to their connector/provider.