"""
Platform-level exceptions for the vnstock plugin architecture.

These exceptions are distinct from the legacy VnstockError hierarchy
in vnstock/core/exceptions.py. They target the new plugin/routing layer.

Hierarchy::

    VnstockPlatformError
    ├── DatasetContractError
    ├── ProviderNotFoundError
    ├── UnsupportedDatasetError
    ├── UnsupportedDatasetForProviderError
    └── ProviderFetchError
"""

from __future__ import annotations


class VnstockPlatformError(Exception):
    """Base exception for the vnstock plugin platform layer."""


class DatasetContractError(VnstockPlatformError):
    """Raised when a dataset contract is missing or invalid.

    Args:
        dataset: The dataset name that caused the error.
        message: Optional detail message.
    """

    def __init__(self, dataset: str, message: str | None = None) -> None:
        self.dataset = dataset
        detail = message or f"Dataset contract error for '{dataset}'."
        super().__init__(detail)


class ProviderNotFoundError(VnstockPlatformError):
    """Raised when a requested provider is not registered.

    Args:
        name: The provider name that was not found.
    """

    def __init__(self, name: str) -> None:
        self.provider_name = name
        super().__init__(f"Provider '{name}' is not registered.")


class UnsupportedDatasetError(VnstockPlatformError):
    """Raised when no registered provider supports the requested dataset.

    Args:
        dataset: The dataset name with no supporting providers.
    """

    def __init__(self, dataset: str) -> None:
        self.dataset = dataset
        super().__init__(f"No registered provider supports dataset '{dataset}'.")


class UnsupportedDatasetForProviderError(VnstockPlatformError):
    """Raised when a specific provider does not support the requested dataset.

    Args:
        provider_name: The provider that was asked.
        dataset: The dataset name that provider does not support.
    """

    def __init__(self, provider_name: str, dataset: str) -> None:
        self.provider_name = provider_name
        self.dataset = dataset
        super().__init__(
            f"Provider '{provider_name}' does not support dataset '{dataset}'."
        )


class ProviderFetchError(VnstockPlatformError):
    """Raised when a provider fails to fetch data.

    Args:
        provider_name: The provider that failed.
        dataset: The dataset that was being fetched.
        cause: The underlying exception, if any.
    """

    def __init__(
        self,
        provider_name: str,
        dataset: str,
        cause: BaseException | None = None,
    ) -> None:
        self.provider_name = provider_name
        self.dataset = dataset
        self.cause = cause
        msg = f"Provider '{provider_name}' failed to fetch dataset '{dataset}'."
        if cause:
            msg += f" Cause: {cause}"
        super().__init__(msg)
