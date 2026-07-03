"""
ProviderRouter for the vnstock plugin platform layer.

Resolves a dataset + source request to a specific ProviderPlugin instance.

Phase 1 routing behavior:

- explicit source: return that provider if it supports the dataset,
  otherwise raise UnsupportedDatasetForProviderError.
- source=None or source="auto": use configured default provider priority
  (defaults to alphabetical order). Return the first supporting provider.

Usage::

    from vnstock.core.provider.plugin_router import PluginRouter
    from vnstock.core.provider.plugin_registry import PluginRegistry

    registry = PluginRegistry()
    registry.register(kbs_plugin)
    registry.register(vci_plugin)

    router = PluginRouter(registry, default_priority=["KBS", "VCI"])

    result = router.resolve("equity.ohlcv")           # auto
    result = router.resolve("equity.ohlcv", source="VCI")   # explicit
    diag = router.last_diagnostics
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vnstock.core.provider.exceptions import (
    UnsupportedDatasetError,
    UnsupportedDatasetForProviderError,
)

if TYPE_CHECKING:
    from vnstock.core.provider.plugin import ProviderPlugin
    from vnstock.core.provider.plugin_registry import PluginRegistry


class PluginRouter:
    """Resolves dataset requests to provider plugin instances.

    Args:
        registry: The :class:`PluginRegistry` to resolve providers from.
        default_priority: Ordered list of provider names to prefer for
            ``source=None`` / ``source="auto"`` routing. Providers not in
            this list are appended in alphabetical order.
    """

    def __init__(
        self,
        registry: "PluginRegistry",
        default_priority: list[str] | None = None,
    ) -> None:
        self.registry = registry
        self.default_priority: list[str] = [n.upper() for n in (default_priority or [])]
        self._last_diagnostics: dict[str, Any] | None = None

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
            params: Optional parameters for future routing extensions
                (unused in Phase 1).

        Returns:
            The resolved :class:`ProviderPlugin`.

        Raises:
            UnsupportedDatasetForProviderError: If an explicit source is
                requested but does not support *dataset*.
            UnsupportedDatasetError: If no registered provider supports
                *dataset* (auto routing).
        """
        params = params or {}

        if source is not None and source.lower() != "auto":
            return self._resolve_explicit(dataset, source)

        return self._resolve_auto(dataset)

    def _resolve_explicit(self, dataset: str, source: str) -> "ProviderPlugin":
        """Resolve to a named provider; verify it supports *dataset*."""
        from vnstock.core.provider.exceptions import ProviderNotFoundError

        try:
            provider = self.registry.get(source)
        except ProviderNotFoundError:
            raise

        caps = provider.capabilities()
        cap = caps.get(dataset)
        if not cap or not cap.get("supported", False):
            raise UnsupportedDatasetForProviderError(provider.name, dataset)

        candidates = self.registry.providers_for(dataset)
        self._last_diagnostics = {
            "dataset": dataset,
            "source": source,
            "selected_provider": provider.name,
            "candidate_providers": [p.name for p in candidates],
            "routing_reason": "explicit source requested",
        }
        return provider

    def _resolve_auto(self, dataset: str) -> "ProviderPlugin":
        """Resolve using configured priority order."""
        candidates = self.registry.providers_for(dataset)
        if not candidates:
            self._last_diagnostics = {
                "dataset": dataset,
                "source": "auto",
                "selected_provider": None,
                "candidate_providers": [],
                "routing_reason": "no candidates found",
            }
            raise UnsupportedDatasetError(dataset)

        # Sort candidates by priority list; providers not in list come last
        # (sorted alphabetically among themselves).
        priority_index = {name: i for i, name in enumerate(self.default_priority)}
        n_prio = len(self.default_priority)

        def sort_key(p: "ProviderPlugin") -> tuple[int, str]:
            idx = priority_index.get(p.name.upper(), n_prio)
            return (idx, p.name.upper())

        ordered = sorted(candidates, key=sort_key)
        selected = ordered[0]

        self._last_diagnostics = {
            "dataset": dataset,
            "source": "auto",
            "selected_provider": selected.name,
            "candidate_providers": [p.name for p in candidates],
            "routing_reason": "selected by default provider priority",
        }
        return selected

    @property
    def last_diagnostics(self) -> dict[str, Any] | None:
        """Diagnostics from the most recent :meth:`resolve` call."""
        return self._last_diagnostics
