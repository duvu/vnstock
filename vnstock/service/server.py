"""Local HTTP data service for vnstock.

Uses Python stdlib ``http.server`` — no extra dependencies needed.

Endpoint routing is handled by :class:`VnstockHandler`.

FORBIDDEN endpoints (must never exist):
  /v1/auth/login
  /v1/order*
  /v1/account*
  /v1/portfolio*
  /v1/transfer*
  /v1/margin*

ALLOWED endpoint groups:
  GET /healthz
  GET /v1/providers
  GET /v1/providers/health
  GET /v1/providers/capabilities
  GET /v1/auth/status
  GET /v1/auth/providers
  GET /v1/market/<dataset>?<params>
  GET /v1/reference/<dataset>?<params>
  GET /v1/fundamental/<dataset>?<params>
  GET /v1/fund/<dataset>?<params>
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Forbidden route prefixes (case-insensitive)
# ---------------------------------------------------------------------------

_FORBIDDEN_PREFIXES = (
    "/v1/auth/login",
    "/v1/order",
    "/v1/account",
    "/v1/portfolio",
    "/v1/transfer",
    "/v1/margin",
)


def _is_forbidden(path: str) -> bool:
    """Return True if path matches a forbidden prefix."""
    p = path.lower().rstrip("/")
    for prefix in _FORBIDDEN_PREFIXES:
        if p == prefix or p.startswith(prefix + "/"):
            return True
    return False


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------


class VnstockHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler for vnstock local data service."""

    # Populated on server instance
    _auth_manager: Any = None

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        logger.debug(f"[service] {format % args}")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        # ── Forbidden gate ────────────────────────────────────────────────
        if _is_forbidden(path):
            self._send_json(
                404,
                {
                    "error": "not_found",
                    "message": f"Endpoint '{path}' does not exist.",
                },
            )
            return

        # ── Route dispatch ────────────────────────────────────────────────
        if path in ("/healthz", "/health"):
            self._handle_healthz()
        elif path == "/v1/providers":
            self._handle_providers()
        elif path == "/v1/providers/health":
            self._handle_providers_health()
        elif path == "/v1/providers/capabilities":
            self._handle_providers_capabilities()
        elif path == "/v1/auth/status":
            self._handle_auth_status()
        elif path == "/v1/auth/providers":
            self._handle_auth_providers()
        elif path.startswith("/v1/market/"):
            self._handle_data("market", path[len("/v1/market/") :], query)
        elif path.startswith("/v1/reference/"):
            self._handle_data("reference", path[len("/v1/reference/") :], query)
        elif path.startswith("/v1/fundamental/"):
            self._handle_data("fundamental", path[len("/v1/fundamental/") :], query)
        elif path.startswith("/v1/fund/"):
            self._handle_data("fund", path[len("/v1/fund/") :], query)
        else:
            self._send_json(
                404,
                {
                    "error": "not_found",
                    "message": f"Endpoint '{path}' not found.",
                },
            )

    # ------------------------------------------------------------------ #
    # Endpoint handlers                                                   #
    # ------------------------------------------------------------------ #

    def _handle_healthz(self) -> None:
        self._send_json(200, {"status": "ok", "service": "vnstock"})

    def _handle_providers(self) -> None:
        try:
            from vnstock.core.registry import ProviderRegistry

            providers = list(ProviderRegistry.list())
        except Exception:
            providers = []
        self._send_json(200, {"providers": providers})

    def _handle_providers_health(self) -> None:
        try:
            from vnstock.core.provider.health import DEFAULT_HEALTH_STORE

            all_providers = DEFAULT_HEALTH_STORE.all_providers()
            health_data = {}
            for pname in all_providers:
                for dataset in DEFAULT_HEALTH_STORE.all_datasets():
                    h = DEFAULT_HEALTH_STORE.get(pname, dataset)
                    if pname not in health_data:
                        health_data[pname] = {}
                    health_data[pname][dataset] = h.to_dict()
        except Exception:
            health_data = {}
        self._send_json(200, {"health": health_data})

    def _handle_providers_capabilities(self) -> None:
        """Return provider capabilities matrix (no auth material)."""
        try:
            from vnstock.core.registry import ProviderRegistry

            caps: dict[str, Any] = {}
            for name in ProviderRegistry.list():
                try:
                    plugin = ProviderRegistry.get(name)
                    caps[name] = plugin.capabilities()
                except Exception:
                    caps[name] = {}
        except Exception:
            caps = {}
        self._send_json(200, {"capabilities": caps})

    def _handle_auth_status(self) -> None:
        """Return safe auth status — no token material."""
        if self._auth_manager is None:
            self._send_json(
                200, {"auth_status": {}, "note": "auth_manager not configured"}
            )
            return
        try:
            status = self._auth_manager.auth_status_all()
            # Strip any token material before returning
            safe_status = {}
            for provider, s in status.items():
                safe_status[provider] = {
                    "authenticated": s.get("authenticated", False),
                    "provider": s.get("provider", provider),
                    "source": s.get("source"),
                }
        except Exception:
            safe_status = {}
        self._send_json(200, {"auth_status": safe_status})

    def _handle_auth_providers(self) -> None:
        """Return which providers support auth (no credential material)."""
        try:
            from vnstock.providers import PROVIDER_PLUGINS

            auth_info: dict[str, Any] = {}
            for name, plugin_class in PROVIDER_PLUGINS.items():
                try:
                    plugin = plugin_class()
                    spec = plugin.auth_spec("equity.ohlcv")
                    auth_info[name] = {
                        "auth_type": spec.auth_type.value,
                        "required": spec.required,
                        "experimental": spec.experimental,
                        "explicit_only": spec.explicit_only,
                    }
                except Exception:
                    auth_info[name] = {"auth_type": "none", "required": False}
        except Exception:
            auth_info = {}
        self._send_json(200, {"auth_providers": auth_info})

    def _handle_data(self, domain: str, dataset: str, query: dict) -> None:
        """Generic data endpoint handler (data-read only)."""
        if not dataset:
            self._send_json(
                400, {"error": "missing_dataset", "message": "Dataset required."}
            )
            return

        # Extract symbol from query params
        symbol_list = query.get("symbol", query.get("symbols", []))
        symbol = symbol_list[0] if symbol_list else None

        try:
            import pandas as pd

            from vnstock import Vnstock

            if symbol:
                vn = Vnstock(symbol=symbol, source="AUTO")
            else:
                vn = Vnstock(source="AUTO")

            # Map domain/dataset to method calls
            data_map = {
                "market": {
                    "ohlcv": lambda: vn.stock.quote.history(
                        start=query.get("start", ["2024-01-01"])[0],
                        end=query.get("end", ["2024-12-31"])[0],
                        interval=query.get("interval", ["1D"])[0],
                    ),
                },
                "reference": {
                    "listing": lambda: vn.stock.listing.all_symbols(),
                },
                "fundamental": {
                    "balance_sheet": lambda: vn.stock.finance.balance_sheet(
                        period=query.get("period", ["annual"])[0],
                    ),
                },
            }

            domain_map = data_map.get(domain, {})
            handler_fn = domain_map.get(dataset)
            if handler_fn is None:
                self._send_json(
                    404,
                    {
                        "error": "not_found",
                        "message": f"Dataset '{domain}/{dataset}' not found.",
                    },
                )
                return

            df = handler_fn()
            if isinstance(df, pd.DataFrame):
                records = df.to_dict(orient="records")
            else:
                records = []
            self._send_json(200, {"data": records, "dataset": f"{domain}/{dataset}"})

        except Exception as exc:
            self._send_json(
                500,
                {
                    "error": "internal_error",
                    "message": str(exc)[:200],
                },
            )

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# Server factory
# ---------------------------------------------------------------------------


def _make_handler(auth_manager: Any = None):
    """Create a handler class with auth_manager bound."""

    class BoundHandler(VnstockHandler):
        _auth_manager = auth_manager

    return BoundHandler


def run_server(
    host: str = "127.0.0.1",
    port: int = 6900,
    auth_manager: Any = None,
    *,
    _stop_event: threading.Event | None = None,
) -> None:
    """Start the vnstock local data service.

    Args:
        host: Bind address. Defaults to ``127.0.0.1`` (localhost-only).
        port: Bind port. Defaults to 6900.
        auth_manager: Optional :class:`AuthManager` for auth status endpoints.
        _stop_event: Internal use only — threading.Event to signal shutdown.
    """
    handler_class = _make_handler(auth_manager)
    server = HTTPServer((host, port), handler_class)
    logger.info(f"vnstock service listening on http://{host}:{port}")

    if _stop_event is not None:
        # Non-blocking for tests
        def _serve():
            while not _stop_event.is_set():
                server.handle_request()
            server.server_close()

        t = threading.Thread(target=_serve, daemon=True)
        t.start()
        return

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        logger.info("vnstock service stopped.")
