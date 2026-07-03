"""
Unit tests for DataResult and DataFrame.attrs metadata propagation.
"""

from datetime import datetime

import pandas as pd
import pytest

from vnstock.core.result import _FORBIDDEN_METADATA_KEYS, DataResult


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "symbol": ["FPT"],
            "time": [pd.Timestamp("2024-01-01")],
            "open": [100.0],
            "high": [105.0],
            "low": [99.0],
            "close": [103.0],
            "volume": [100000.0],
        }
    )


class TestDataResultMetadataPropagation:
    """Tasks 53-55: Metadata propagation via to_dataframe()."""

    def test_to_dataframe_returns_dataframe(self, sample_df):
        result = DataResult(dataset="equity.ohlcv", provider="KBS", data=sample_df)
        df = result.to_dataframe()
        assert isinstance(df, pd.DataFrame)

    def test_dataset_in_attrs(self, sample_df):
        """Task 53: dataset is attached to DataFrame.attrs."""
        result = DataResult(dataset="equity.ohlcv", provider="KBS", data=sample_df)
        df = result.to_dataframe()
        assert df.attrs["dataset"] == "equity.ohlcv"

    def test_provider_in_attrs(self, sample_df):
        result = DataResult(dataset="equity.ohlcv", provider="KBS", data=sample_df)
        df = result.to_dataframe()
        assert df.attrs["provider"] == "KBS"

    def test_quality_status_in_attrs(self, sample_df):
        result = DataResult(
            dataset="equity.ohlcv",
            provider="KBS",
            data=sample_df,
            quality_status="PASS",
        )
        df = result.to_dataframe()
        assert df.attrs["quality_status"] == "PASS"

    def test_quality_key_backward_compat(self, sample_df):
        """Task 54: df.attrs['quality'] is set for backward compatibility."""
        report = {"checks": []}
        result = DataResult(
            dataset="equity.ohlcv",
            provider="KBS",
            data=sample_df,
            quality_report=report,
        )
        df = result.to_dataframe()
        assert df.attrs["quality"] == report

    def test_empty_quality_report(self, sample_df):
        """Task 54: Empty quality report is still set in attrs."""
        result = DataResult(dataset="equity.ohlcv", provider="KBS", data=sample_df)
        df = result.to_dataframe()
        # quality_report defaults to empty dict — should be in attrs
        assert "quality" in df.attrs

    def test_diagnostics_in_attrs(self, sample_df):
        """Task 55: Diagnostics are attached to DataFrame.attrs."""
        diag = {"routing_reason": "default priority", "selected_provider": "KBS"}
        result = DataResult(
            dataset="equity.ohlcv",
            provider="KBS",
            data=sample_df,
            diagnostics=diag,
        )
        df = result.to_dataframe()
        assert df.attrs["diagnostics"] == diag

    def test_fetched_at_in_attrs(self, sample_df):
        ts = datetime(2024, 1, 1, 12, 0, 0)
        result = DataResult(
            dataset="equity.ohlcv",
            provider="KBS",
            data=sample_df,
            fetched_at=ts,
        )
        df = result.to_dataframe()
        assert df.attrs["fetched_at"] == ts

    def test_ingestion_run_id_in_attrs(self, sample_df):
        result = DataResult(
            dataset="equity.ohlcv",
            provider="KBS",
            data=sample_df,
            ingestion_run_id="run-abc-123",
        )
        df = result.to_dataframe()
        assert df.attrs["ingestion_run_id"] == "run-abc-123"


class TestNoSecretsInMetadata:
    """Task 52: Auth secrets must not be in DataResult or DataFrame.attrs."""

    def test_forbidden_keys_defined(self):
        """Forbidden metadata keys set is non-empty."""
        assert len(_FORBIDDEN_METADATA_KEYS) > 0

    def test_password_not_in_forbidden_keys_not_in_result(self, sample_df):
        """'password' is listed in forbidden keys."""
        assert "password" in _FORBIDDEN_METADATA_KEYS

    def test_access_token_forbidden(self):
        assert "access_token" in _FORBIDDEN_METADATA_KEYS

    def test_dataresult_does_not_accept_token_field(self, sample_df):
        """DataResult has no token/password/api_key field."""
        result = DataResult(dataset="equity.ohlcv", provider="KBS", data=sample_df)
        result_dict = result.__dict__
        for forbidden in _FORBIDDEN_METADATA_KEYS:
            assert forbidden not in result_dict, (
                f"Forbidden key '{forbidden}' found in DataResult"
            )
