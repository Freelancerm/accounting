"""Domain-specific exceptions."""

from __future__ import annotations


class DomainError(ValueError):
    """Base error for invalid domain input or invalid accounting state."""


class InvalidDomainInputError(DomainError):
    """Raised when entity or value object input is invalid."""


class InvalidPostingError(DomainError):
    """Raised when posting logic would create invalid accounting entry."""
