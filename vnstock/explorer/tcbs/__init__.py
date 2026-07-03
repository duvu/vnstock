"""TCBS data explorer module.

SCOPE / SAFETY GATE
-------------------
This module exposes **read-only market-data** endpoints from TCBS public APIs.
It does NOT implement any broker, account, order, portfolio, iCopy, margin,
or transfer operations.  Those APIs require authentication and fall outside
the scope of vnstock.

Vendor-derived fields (ratings, signals, analyst recommendations) are surfaced
as-is from the upstream response under explicit ``vendor_*`` or ``signal_*``
column names.  They are NOT investment advice.  Callers should treat them as
raw data from the data provider.

TCBS is NOT the default provider for any vnstock UI method.  Pass
``source='tcbs'`` explicitly to route calls here.

Unofficial public endpoints — the API contract may drift without notice.
"""

from vnstock.explorer.tcbs.company import Company  # noqa: E402
from vnstock.explorer.tcbs.financial import Finance  # noqa: E402
from vnstock.explorer.tcbs.listing import Listing  # noqa: E402
from vnstock.explorer.tcbs.quote import Quote  # noqa: E402
from vnstock.explorer.tcbs.screener import Screener  # noqa: E402
from vnstock.explorer.tcbs.trading import Trading  # noqa: E402

__all__ = ["Quote", "Trading", "Company", "Finance", "Listing", "Screener"]
