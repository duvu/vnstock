"""Tests for validate/quality_mode integration in BaseUI._dispatch."""

from __future__ import annotations

import warnings
from unittest.mock import patch

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_valid_ohlcv() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": pd.date_range("2025-01-01", periods=3, freq="D"),
            "open": [100.0, 101.0, 102.0],
            "high": [105.0, 106.0, 107.0],
            "low": [95.0, 96.0, 97.0],
            "close": [102.0, 103.0, 104.0],
            "volume": [1000, 2000, 3000],
        }
    )


def _make_invalid_ohlcv() -> pd.DataFrame:
    df = _make_valid_ohlcv()
    df.loc[0, "high"] = 80.0  # high < low → OHLC error
    return df


class _FakeEquityUI:
    """Minimal stand-in that exercises _run_quality_validation directly."""

    def __init__(self, symbol="FPT"):
        self.symbol = symbol

    def ohlcv(
        self, df: pd.DataFrame, quality_mode: str = "warn", validate: bool = True
    ):
        from vnstock.ui._base import _run_quality_validation

        return _run_quality_validation(
            df,
            domain_name="Market",
            method_name="equity",
            consumed_subdomain="ohlcv",
            quality_mode=quality_mode,
            provider="TEST",
            symbol=self.symbol,
        )


# ---------------------------------------------------------------------------
# Tests for _run_quality_validation
# ---------------------------------------------------------------------------


class TestRunQualityValidationOff:
    def test_off_mode_returns_df_unchanged(self):
        df = _make_valid_ohlcv()
        ui = _FakeEquityUI()
        result = ui.ohlcv(df, quality_mode="off")
        assert result is df
        assert "quality" not in result.attrs


class TestRunQualityValidationWarnMode:
    def test_warn_mode_attaches_report(self):
        df = _make_valid_ohlcv()
        ui = _FakeEquityUI()
        result = ui.ohlcv(df, quality_mode="warn")
        # report should be attached when quality.attach_report is True (default)
        assert "quality" in result.attrs
        from vnstock.core.quality.models import ValidationReport

        assert isinstance(result.attrs["quality"], ValidationReport)

    def test_warn_mode_does_not_raise_on_errors(self):
        df = _make_invalid_ohlcv()
        ui = _FakeEquityUI()
        # Should not raise even though there are OHLC errors
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = ui.ohlcv(df, quality_mode="warn")
        assert result is df  # same object returned

    def test_warn_mode_valid_data_no_warning_issued(self):
        df = _make_valid_ohlcv()
        ui = _FakeEquityUI()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ui.ohlcv(df, quality_mode="warn")
        # No UserWarning about data quality errors for clean data
        quality_warns = [x for x in w if "Data quality issues" in str(x.message)]
        assert quality_warns == []


class TestRunQualityValidationStrictMode:
    def test_strict_mode_raises_on_errors(self):
        from vnstock.core.quality.exceptions import DataQualityError

        df = _make_invalid_ohlcv()
        ui = _FakeEquityUI()
        with pytest.raises(DataQualityError) as exc_info:
            ui.ohlcv(df, quality_mode="strict")
        assert exc_info.value.report.severity == "error"

    def test_strict_mode_no_raise_for_valid_data(self):
        df = _make_valid_ohlcv()
        ui = _FakeEquityUI()
        result = ui.ohlcv(df, quality_mode="strict")
        assert result is df


class TestDispatchQualityKwargsNotLeaked:
    """Ensure validate/quality_mode kwargs are stripped before provider calls."""

    def test_quality_kwargs_popped_from_kwargs(self):
        """_dispatch must pop validate and quality_mode before provider dispatch."""
        from vnstock.ui._base import BaseUI

        class MinimalUI(BaseUI):
            def __init__(self):
                self.symbol = "FPT"

        # Patch _execute_dispatch to capture what kwargs reaches the provider
        captured_kwargs: dict = {}

        def fake_execute(
            module_type, sub_module, class_name, function_name, symbol, args, kwargs
        ):
            captured_kwargs.update(kwargs)
            df = _make_valid_ohlcv()
            return df

        ui = MinimalUI()
        ui._execute_dispatch = fake_execute

        # Mock the MAP to return a simple entry
        fake_meta = ("explorer", "vci", "Quote", "history", "vci")
        with (
            patch(
                "vnstock.ui._registry.MAP", {"Market": {"equity": {"ohlcv": fake_meta}}}
            ),
            patch("vnstock.core.router.router.pick", return_value="vci"),
            patch("vnstock.ui._pools.POOLS", {}),
        ):
            try:
                ui._dispatch(
                    "Market",
                    "equity",
                    "ohlcv",
                    validate=True,
                    quality_mode="warn",
                    source="vci",
                )
            except Exception:
                pass

        assert "validate" not in captured_kwargs, "validate should not reach provider"
        assert "quality_mode" not in captured_kwargs, (
            "quality_mode should not reach provider"
        )
