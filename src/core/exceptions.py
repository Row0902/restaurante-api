"""Domain exception hierarchy for the core layer.

No HTTP knowledge. API layer translates these to HTTP status codes.
"""


class DomainError(Exception):
    """Base exception for all domain errors."""


class MenuNotFoundError(DomainError):
    """Raised when a menu item is not found by its ID."""

    def __init__(self, plato_id: int | str) -> None:
        """Initialize with the menu item ID that was not found."""
        self.plato_id = plato_id
        super().__init__(f"Menu item {plato_id} not found.")


class InvalidMenuDataError(DomainError):
    """Raised when menu data fails validation."""

    def __init__(self, field: str, message: str) -> None:
        """Initialize with the field name and validation message."""
        self.field = field
        self.message = message
        super().__init__(f"{field} {message}")


class OrdenNotFoundError(DomainError):
    """Raised when an order is not found by its ID."""

    def __init__(self, orden_id: int) -> None:
        """Initialize with the order ID that was not found."""
        self.orden_id = orden_id
        super().__init__(f"Order {orden_id} not found.")


class InvalidOrdenDataError(DomainError):
    """Raised when order data fails validation."""

    def __init__(self, field: str, message: str) -> None:
        """Initialize with the field name and validation message."""
        self.field = field
        self.message = message
        super().__init__(f"{field} {message}")


class InvalidEstadoTransitionError(DomainError):
    """Raised when an invalid estado transition is attempted."""

    def __init__(self, actual: str, intentado: str) -> None:
        """Initialize with the current and attempted estado values."""
        self.actual = actual
        self.intentado = intentado
        super().__init__(f"Cannot transition from {actual} to {intentado}.")
