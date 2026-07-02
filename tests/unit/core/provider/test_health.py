"""Tests for provider health scoring (vnstock/core/provider/health.py)."""

from __future__ import annotations

from datetime import datetime, timezone

from vnstock.core.provider.health import aggregate_health, score_health
from vnstock.core.provider.models import ProviderIssue


def _issue(severity: str) -> ProviderIssue:
    return ProviderIssue(
        code=f"TEST_{severity.upper()}",
        severity=severity,
        provider="test",
        capability="ohlcv",
        message=f"Test {severity} issue.",
    )


class TestScoreHealthStatus:
    """Status should reflect the worst issue severity."""

    def test_no_issues_is_healthy(self):
        health = score_health("vci", [])
        assert health.status == "healthy"
        assert health.provider == "vci"

    def test_info_only_is_healthy(self):
        health = score_health("vci", [_issue("info")])
        assert health.status == "healthy"

    def test_warning_is_degraded(self):
        health = score_health("vci", [_issue("warning")])
        assert health.status == "degraded"

    def test_error_is_failing(self):
        health = score_health("vci", [_issue("error")])
        assert health.status == "failing"

    def test_multiple_warnings_is_degraded(self):
        health = score_health("vci", [_issue("warning")] * 3)
        assert health.status == "degraded"

    def test_error_trumps_warning(self):
        health = score_health("vci", [_issue("warning"), _issue("error")])
        assert health.status == "failing"


class TestScoreHealthLatency:
    """Latency thresholds affect health status."""

    def test_fast_latency_healthy(self):
        health = score_health("vci", [], latency_ms=200.0)
        assert health.status == "healthy"
        assert health.latency_ms == 200.0

    def test_slow_latency_degraded(self):
        health = score_health("vci", [], latency_ms=5000.0)
        assert health.status == "degraded"

    def test_very_slow_latency_failing(self):
        health = score_health("vci", [], latency_ms=15000.0)
        assert health.status == "failing"


class TestScoreHealthErrorRate:
    """Error rate thresholds affect health status."""

    def test_low_error_rate_healthy(self):
        health = score_health("vci", [], error_rate=0.02)
        assert health.status == "healthy"
        assert health.error_rate == 0.02

    def test_moderate_error_rate_degraded(self):
        health = score_health("vci", [], error_rate=0.20)
        assert health.status == "degraded"

    def test_high_error_rate_failing(self):
        health = score_health("vci", [], error_rate=0.60)
        assert health.status == "failing"


class TestScoreHealthMetadata:
    """Metadata is correctly stored."""

    def test_schema_status_stored(self):
        health = score_health("kbs", [], schema_status="drifted")
        assert health.schema_status == "drifted"

    def test_freshness_status_stored(self):
        health = score_health("kbs", [], freshness_status="stale")
        assert health.freshness_status == "stale"

    def test_capabilities_checked_stored(self):
        health = score_health(
            "vci", [], capabilities_checked=["ohlcv/equity", "price_board/equity"]
        )
        assert health.capabilities_checked == ["ohlcv/equity", "price_board/equity"]

    def test_capabilities_checked_default_is_empty_list(self):
        health = score_health("vci", [])
        assert health.capabilities_checked == []

    def test_custom_timestamp_stored(self):
        ts = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        health = score_health("vci", [], checked_at=ts)
        assert health.checked_at == ts

    def test_default_timestamp_is_recent(self):
        before = datetime.now(tz=timezone.utc)
        health = score_health("vci", [])
        after = datetime.now(tz=timezone.utc)
        assert before <= health.checked_at <= after

    def test_issues_stored(self):
        issues = [_issue("warning"), _issue("info")]
        health = score_health("vci", issues)
        assert len(health.issues) == 2

    def test_to_dict_serializable(self):
        health = score_health("vci", [_issue("warning")])
        d = health.to_dict()
        assert isinstance(d, dict)
        assert d["provider"] == "vci"
        assert d["status"] == "degraded"
        assert "checked_at" in d

    def test_to_json_string(self):
        health = score_health("vci", [])
        j = health.to_json()
        assert isinstance(j, str)
        assert "healthy" in j


class TestAggregateHealth:
    """aggregate_health summarizes multiple snapshots correctly."""

    def test_all_healthy(self):
        snaps = [
            score_health("vci", []),
            score_health("kbs", []),
        ]
        summary = aggregate_health(snaps)
        assert set(summary["providers"]) == {"vci", "kbs"}
        assert set(summary["healthy"]) == {"vci", "kbs"}
        assert summary["degraded"] == []
        assert summary["failing"] == []
        assert summary["total_issues"] == 0

    def test_mixed_statuses(self):
        snaps = [
            score_health("vci", []),
            score_health("kbs", [_issue("warning")]),
            score_health("dnse", [_issue("error")]),
        ]
        summary = aggregate_health(snaps)
        assert "vci" in summary["healthy"]
        assert "kbs" in summary["degraded"]
        assert "dnse" in summary["failing"]

    def test_total_issues_count(self):
        snaps = [
            score_health("vci", [_issue("warning"), _issue("info")]),
            score_health("kbs", [_issue("error")]),
        ]
        summary = aggregate_health(snaps)
        assert summary["total_issues"] == 3
