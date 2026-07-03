"""
ProviderRouter for the vnstock plugin platform layer.

Resolves a dataset + source request to a specific ProviderPlugin instance,
taking into account provider health, cooldown state, and routing policy.

Phase 3 routing behavior
------------------------

**Auto routing** (``source=None`` or ``source="auto"``)

1. Collect all providers that support the dataset.
2. Filter by health status according to :class:`RoutingPolicy`:
   - DISABLED providers are always excluded.
   - Cooled-down providers are excluded when ``respect_cooldown=True``.
   - FAILING providers are excluded unless ``allow_failing_fallback=True``.
   - When ``prefer_healthy=True``, HEALTHY providers are tried first.
   - When ``allow_degraded=True``, DEGRADED providers are a fallback tier.
3. Within each tier, break ties using the dataset-level priority list from
   :data:`~vnstock.core.provider.routing.DEFAULT_PROVIDER_PRIORITY`.
4. Raise :class:`~vnstock.core.provider.exceptions.NoHealthyProviderError`
   if no provider passes the filters.

**Explicit routing** (``source="KBS"`` etc.)

1. Look up the named provider.
2. Verify it supports the dataset.
3. If DISABLED → raise :class:`ProviderDisabledError`.
4. If in cooldown and ``respect_cooldown=True`` → raise
   :class:`ProviderInCooldownError`.
5. If DEGRADED or FAILING → add a warning to diagnostics but still return
   the provider (the caller asked explicitly).

Usage::

    from vnstock.core.provider.plugin_router import PluginRouter
    from vnstock.core.provider.plugin_registry import PluginRegistry
    from vnstock.core.provider.health import InMemoryProviderHealthStore
    from vnstock.core.provider.routing import RoutingPolicy

    registry = PluginRegistry()
    registry.register(kbs_plugin)
    registry.register(vci_plugin)

    store = InMemoryProviderHealthStore()
    policy = RoutingPolicy.default()

    router = PluginRouter(registry, health_store=store, policy=policy)

    provider = router.resolve("equity.ohlcv")           # auto
    provider = router.resolve("equity.ohlcv", source="VCI")   # explicit
    decision = router.last_decision
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vnstock.core.provider.exceptions import (
    NoHealthyProviderError,
    ProviderDisabledError,
    ProviderInCooldownError,
    UnsupportedDatasetError,
    UnsupportedDatasetForProviderError,
)
from vnstock.core.provider.health import (
    DEFAULT_HEALTH_STORE,
    HealthStatus,
    InMemoryProviderHealthStore,
)
from vnstock.core.provider.routing import (
    DEFAULT_PROVIDER_PRIORITY,
    RoutingDecision,
    RoutingPolicy,
)

if TYPE_CHECKING:
    from vnstock.core.provider.plugin import ProviderPlugin
    from vnstock.core.provider.plugin_registry import PluginRegistry


class PluginRouter:
    """Resolves dataset requests to provider plugin instances.

    Args:
        registry: The :class:`PluginRegistry` to resolve providers from.
        default_priority: Ordered list of provider names to prefer for
            ``source=None`` / ``source="auto"`` routing. When ``None``,
            per-dataset priorities from :data:`DEFAULT_PROVIDER_PRIORITY`
            are used.  Providers not in the list are appended alphabetically.
        health_store: Health store to read and update.  Defaults to the
            module-level :data:`~vnstock.core.provider.health.DEFAULT_HEALTH_STORE`.
        policy: Routing policy controlling health-aware behavior.  Defaults
            to :meth:`RoutingPolicy.default`.
    """

    def __init__(
        self,
        registry: "PluginRegistry",
        default_priority: list[str] | None = None,
        health_store: InMemoryProviderHealthStore | None = None,
        policy: RoutingPolicy | None = None,
    ) -> None:
        self.registry = registry
        self.default_priority: list[str] | None = (
            [n.upper() for n in default_priority] if default_priority else None
        )
        self.health_store = (
            health_store if health_store is not None else DEFAULT_HEALTH_STORE
        )
        self.policy: RoutingPolicy = policy or RoutingPolicy.default()
        self._last_decision: RoutingDecision | None = None

    def resolve(
        self,
        dataset: str,
        source: str | None = None,
        params: dict | None = None,
    ) -> "ProviderPlugin":
        """Resolve *dataset* to a provider plugin.

        Args:
            dataset: Dotted dataset name, e.g. ``"equity.ohlcv"``.
            source: Provider name (explicit) or ``None`` / ``"auto"``
                for automatic selection.
            params: Optional parameters for future routing extensions.

        Returns:
            The resolved :class:`ProviderPlugin`.

        Raises:
            ProviderNotFoundError: Explicit source not registered.
            UnsupportedDatasetForProviderError: Explicit source registered
                but does not support *dataset*.
            ProviderDisabledError: Explicit source is DISABLED.
            ProviderInCooldownError: Explicit source is in cooldown and
                ``policy.respect_cooldown`` is True.
            NoHealthyProviderError: Auto routing found no healthy candidate.
            UnsupportedDatasetError: Auto routing found no candidates at all.
        """
        params = params or {}

        if source is not None and source.lower() != "auto":
            return self._resolve_explicit(dataset, source)

        return self._resolve_auto(dataset)

    # ------------------------------------------------------------------ #
    # Explicit routing                                                     #
    # ------------------------------------------------------------------ #

    def _resolve_explicit(self, dataset: str, source: str) -> "ProviderPlugin":
        """Resolve to a named provider with health checks."""
        from vnstock.core.provider.exceptions import ProviderNotFoundError

        try:
            provider = self.registry.get(source)
        except ProviderNotFoundError:
            raise

        caps = provider.capabilities()
        cap = caps.get(dataset)
        if not cap or not cap.get("supported", False):
            raise UnsupportedDatasetForProviderError(provider.name, dataset)

        health = self.health_store.get(provider.name, dataset)
        warnings: list[str] = []

        # DISABLED always blocks even explicit requests
        if health.status == HealthStatus.DISABLED:
            raise ProviderDisabledError(provider.name, dataset, notes=health.notes)

        # Cooldown blocks explicit requests when policy says so
        if self.policy.respect_cooldown and health.is_in_cooldown():
            raise ProviderInCooldownError(
                provider.name,
                dataset,
                cooldown_until=health.cooldown_until.isoformat()
                if health.cooldown_until
                else None,
            )

        # Warn on degraded/failing but still honour the explicit request
        if health.status == HealthStatus.FAILING:
            warnings.append(
                f"Provider '{provider.name}' is FAILING for dataset '{dataset}'. "
                "Proceeding because source was explicitly requested."
            )
        elif health.status == HealthStatus.DEGRADED:
            warnings.append(
                f"Provider '{provider.name}' is DEGRADED for dataset '{dataset}'."
            )

        candidates = self.registry.providers_for(dataset)
        decision = RoutingDecision(
            dataset=dataset,
            requested_source=source,
            selected_provider=provider.name,
            candidates=[p.name for p in candidates],
            rejected={},
            fallback=False,
            reason="explicit source requested",
            health_snapshot=self._build_health_snapshot([provider], dataset),
            warnings=warnings,
        )
        self._last_decision = decision
        return provider

    # ------------------------------------------------------------------ #
    # Auto routing                                                         #
    # ------------------------------------------------------------------ #

    def _resolve_auto(self, dataset: str) -> "ProviderPlugin":
        """Resolve using health status and configured priority order."""
        all_candidates = self.registry.providers_for(dataset)
        if not all_candidates:
            decision = RoutingDecision(
                dataset=dataset,
                requested_source=None,
                selected_provider=None,
                candidates=[],
                rejected={},
                reason="no providers registered for this dataset",
            )
            self._last_decision = decision
            raise UnsupportedDatasetError(dataset)

        # Build priority lookup
        priority_list = self.default_priority or DEFAULT_PROVIDER_PRIORITY.get(
            dataset, []
        )
        priority_index = {name.upper(): i for i, name in enumerate(priority_list)}
        n_prio = len(priority_list)

        def sort_key(p: "ProviderPlugin") -> tuple[int, str]:
            idx = priority_index.get(p.name.upper(), n_prio)
            return (idx, p.name.upper())

        ordered = sorted(all_candidates, key=sort_key)

        # Bucket providers by health tier
        healthy: list["ProviderPlugin"] = []
        degraded: list["ProviderPlugin"] = []
        failing: list["ProviderPlugin"] = []
        rejected: dict[str, str] = {}

        for p in ordered:
            h = self.health_store.get(p.name, dataset)
            if h.status == HealthStatus.DISABLED:
                rejected[p.name] = "DISABLED"
                continue
            if self.policy.respect_cooldown and h.is_in_cooldown():
                rejected[p.name] = "cooldown active"
                continue
            if h.status in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN):
                healthy.append(p)
            elif h.status == HealthStatus.DEGRADED:
                degraded.append(p)
            elif h.status == HealthStatus.FAILING:
                failing.append(p)

        # Select from highest-quality available tier
        selected: "ProviderPlugin | None" = None
        fallback = False
        reason = ""
        warnings: list[str] = []

        if self.policy.prefer_healthy and healthy:
            selected = healthy[0]
            reason = "selected by health-aware default priority (HEALTHY/UNKNOWN)"
        elif self.policy.allow_degraded and degraded:
            selected = degraded[0]
            fallback = True
            reason = "fallback to DEGRADED provider (no HEALTHY provider available)"
            warnings.append(
                f"Provider '{selected.name}' is DEGRADED for dataset '{dataset}'."
            )
        elif self.policy.allow_failing_fallback and failing:
            selected = failing[0]
            fallback = True
            reason = "last-resort fallback to FAILING provider"
            warnings.append(
                f"Provider '{selected.name}' is FAILING for dataset '{dataset}'. "
                "allow_failing_fallback is enabled."
            )

        health_snapshot = self._build_health_snapshot(all_candidates, dataset)
        decision = RoutingDecision(
            dataset=dataset,
            requested_source=None,
            selected_provider=selected.name if selected else None,
            candidates=[p.name for p in all_candidates],
            rejected=rejected,
            fallback=fallback,
            reason=reason,
            health_snapshot=health_snapshot,
            warnings=warnings,
        )
        self._last_decision = decision

        if selected is None:
            raise NoHealthyProviderError(
                dataset,
                candidates=[p.name for p in all_candidates],
                rejection_reasons=rejected,
            )

        return selected

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _build_health_snapshot(
        self,
        providers: "list[ProviderPlugin]",
        dataset: str,
    ) -> dict[str, Any]:
        return {
            p.name: self.health_store.get(p.name, dataset).to_dict() for p in providers
        }

    def record_success(
        self,
        provider: str,
        dataset: str,
        latency_ms: float | None = None,
        freshness_score: float | None = None,
    ) -> None:
        """Record a successful fetch to update health state.

        Args:
            provider: Provider name.
            dataset: Dataset name.
            latency_ms: Optional fetch latency in milliseconds.
            freshness_score: Optional freshness score in ``[0.0, 1.0]``.
        """
        self.health_store.record_success(
            provider, dataset, latency_ms=latency_ms, freshness_score=freshness_score
        )

    def record_failure(
        self,
        provider: str,
        dataset: str,
        notes: str | None = None,
        failure_threshold: int | None = None,
        cooldown_seconds: float | None = None,
    ) -> None:
        """Record a fetch failure to update health state.

        Args:
            provider: Provider name.
            dataset: Dataset name.
            notes: Optional human-readable failure notes.
            failure_threshold: Override default consecutive-failure threshold.
            cooldown_seconds: Override default cooldown window.
        """
        self.health_store.record_failure(
            provider,
            dataset,
            notes=notes,
            failure_threshold=failure_threshold,
            cooldown_seconds=cooldown_seconds,
        )

    # ------------------------------------------------------------------ #
    # Properties                                                           #
    # ------------------------------------------------------------------ #

    @property
    def last_diagnostics(self) -> dict[str, Any] | None:
        """Diagnostics from the most recent :meth:`resolve` call (legacy key)."""
        if self._last_decision is None:
            return None
        return self._last_decision.to_dict()

    @property
    def last_decision(self) -> RoutingDecision | None:
        """Full :class:`RoutingDecision` from the most recent :meth:`resolve` call."""
        return self._last_decision
