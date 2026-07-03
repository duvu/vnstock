"""
Fake provider plugin for use in unit tests.

Do NOT import this in production code.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


class FakeProviderPlugin:
    """Minimal provider plugin for testing ProviderRegistry and ProviderRouter.

    Supports ``equity.ohlcv`` and ``equity.quote`` as stable datasets.
    """

    def __init__(self, name: str, supported_datasets: list[str] | None = None) -> None:
        self.name = name
        self._supported: list[str] = supported_datasets or [
            "equity.ohlcv",
            "equity.quote",
        ]

    def capabilities(self) -> dict[str, Any]:
        return {
            ds: {
                "supported": True,
                "status": "stable",
                "auth_required": False,
                "intervals": ["1D"] if "ohlcv" in ds else [],
            }
            for ds in self._supported
        }

    def fetch(self, dataset: str, params: dict[str, Any]) -> pd.DataFrame:
        from vnstock.core.provider.exceptions import UnsupportedDatasetForProviderError

        if dataset not in self._supported:
            raise UnsupportedDatasetForProviderError(self.name, dataset)
        # Return empty DataFrame with minimal contract columns
        if dataset == "equity.ohlcv":
            return pd.DataFrame(
                columns=["symbol", "time", "open", "high", "low", "close", "volume"]
            )
        return pd.DataFrame(columns=["symbol"])

    def validate_params(self, dataset: str, params: dict[str, Any]) -> None:
        pass

    def diagnostics(self) -> dict[str, Any]:
        return {"name": self.name, "status": "ok"}
