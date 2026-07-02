"""Provider health scoring.

Derives a ProviderHealth snapshot from a list of ProviderIssue objects
and optional latency/row-count inputs. Does NOT call live endpoints —
it scores health from already-collected evidence (drift issues, comparison
issues, latency measurements, etc.).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from vnstock.core.provider.models import ProviderHealth, ProviderIssue

# Scoring weights
_ERROR_PENALTY = 40
_WARNING_PENALTY = 10
_INFO_PENALTY = 0

# Latency thresholds (ms)
_LATENCY_WARN_MS = 3000
_LATENCY_FAIL_MS = 10000

# Error-rate thresholds (0.0–1.0)
_ERROR_RATE_WARN = 0.10
_ERROR_RATE_FAIL = 0.50


def _score_from_issues(issues: list[ProviderIssue]) -> int:
    """Compute a penalty score (0 = healthy). Higher = worse."""
    penalty = 0
    for issue in issues:
        if issue.severity == "error":
            penalty += _ERROR_PENALTY
        elif issue.severity == "warning":
            penalty += _WARNING_PENALTY
        elif issue.severity == "info":
            penalty += _INFO_PENALTY
    return penalty


def _status_from_score(
    score: int,
    latency_ms: float | None,
    error_rate: float | None,
) -> str:
    """Map penalty score + latency + error_rate to status string."""
    # Hard-fail on error rate
    if error_rate is not None and error_rate >= _ERROR_RATE_FAIL:
        return "failing"

    # Hard-fail on latency
    if latency_ms is not None and latency_ms >= _LATENCY_FAIL_MS:
        return "failing"

    if score >= _ERROR_PENALTY:
        return "failing"
    if score >= _WARNING_PENALTY:
        return "degraded"

    # Soft warnings from latency / error rate
    if latency_ms is not None and latency_ms >= _LATENCY_WARN_MS:
        return "degraded"
    if error_rate is not None and error_rate >= _ERROR_RATE_WARN:
        return "degraded"

    return "healthy"


def score_health(
    provider: str,
    issues: list[ProviderIssue],
    *,
    latency_ms: float | None = None,
    error_rate: float | None = None,
    schema_status: str = "unknown",
    freshness_status: str = "unknown",
    capabilities_checked: list[str] | None = None,
    checked_at: datetime | None = None,
) -> ProviderHealth:
    """Derive a ProviderHealth snapshot from evidence.

    Parameters
    ----------
    provider:
        Provider name string.
    issues:
        List of ProviderIssue objects collected from drift/comparison/smoke checks.
    latency_ms:
        Optional measured latency in milliseconds.
    error_rate:
        Optional fraction of recent requests that errored (0.0–1.0).
    schema_status:
        "ok" | "drifted" | "unknown".
    freshness_status:
        "fresh" | "stale" | "unknown".
    capabilities_checked:
        List of capability keys tested in this health check (e.g. ``["ohlcv/equity"]``).
        Pass ``None`` or omit for unknown / not applicable.
    checked_at:
        Timestamp of the check; defaults to utcnow().

    Returns
    -------
    ProviderHealth
    """
    if checked_at is None:
        checked_at = datetime.now(tz=timezone.utc)

    score = _score_from_issues(issues)
    status = _status_from_score(score, latency_ms, error_rate)

    return ProviderHealth(
        provider=provider,
        status=status,
        checked_at=checked_at,
        capabilities_checked=list(capabilities_checked)
        if isinstance(capabilities_checked, (list, tuple))
        else [],
        latency_ms=latency_ms,
        error_rate=error_rate,
        schema_status=schema_status,
        freshness_status=freshness_status,
        issues=list(issues),
    )


def aggregate_health(snapshots: list[ProviderHealth]) -> dict[str, Any]:
    """Aggregate multiple ProviderHealth snapshots into a summary dict.

    Returns a dict with keys:
    - providers: list of provider names
    - healthy: list of healthy provider names
    - degraded: list of degraded provider names
    - failing: list of failing provider names
    - unknown: list of unknown status provider names
    - total_issues: total issue count across all providers
    """
    result: dict[str, Any] = {
        "providers": [],
        "healthy": [],
        "degraded": [],
        "failing": [],
        "unknown": [],
        "total_issues": 0,
    }
    for snap in snapshots:
        result["providers"].append(snap.provider)
        result[snap.status].append(snap.provider)
        result["total_issues"] += len(snap.issues)
    return result
