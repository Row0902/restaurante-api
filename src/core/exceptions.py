"""Domain-specific exceptions for the restaurant API."""


class DomainError(Exception):
    """Base exception for all domain errors."""


class NotFoundError(DomainError):
    """Raised when a requested entity is not found."""
