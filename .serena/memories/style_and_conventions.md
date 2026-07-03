# Style And Conventions
- Ruff is the local formatter/linter source of truth: line length 88, target `py310`, double quotes, lint families `E/W/F/I/B/C4`, `E501` ignored.
- Preserve lazy imports and `TYPE_CHECKING` blocks in `vnstock/ui` to avoid circular imports. Domain accessor methods intentionally import subdomain classes at runtime.
- New user-facing APIs should go through `vnstock/ui`; leaf UI methods route via `BaseUI._dispatch()` and `vnstock/ui/_registry.py::MAP`.
- Keep extraction/API logic in provider modules, not UI methods.
- Provider modules self-register at import time with `vnstock.core.registry.ProviderRegistry.register(provider_type, source, Class)`; add providers by registration and MAP entries rather than UI source `if/else` branches.
- Do not confuse active `vnstock.core.registry.ProviderRegistry` used by `vnstock/base.py::BaseAdapter` with the separate decorator-style registry in `vnstock/core/base/registry.py`.
- Do not add third-party dependencies without explicit approval; there is no lockfile.