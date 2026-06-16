"""Tests for the Orden domain exceptions.

Following Strict TDD: RED phase — test written before production code.
"""

from core.exceptions import (
    DomainError,
    InvalidEstadoTransitionError,
    InvalidOrdenDataError,
    OrdenNotFoundError,
)


class TestOrdenNotFoundError:
    """OrdenNotFoundError carries a descriptive message formatted from orden_id."""

    def test_inherits_from_domain_error(self):
        """OrdenNotFoundError inherits from DomainError."""
        assert issubclass(OrdenNotFoundError, DomainError)

    def test_str_with_integer_id(self):
        """str(e) formats orden_id as int."""
        exc = OrdenNotFoundError(orden_id=99)
        assert str(exc) == "Order 99 not found."

    def test_str_with_different_id(self):
        """str(e) works with different orden_id values."""
        exc = OrdenNotFoundError(orden_id=1)
        assert "1" in str(exc)

    def test_preserves_orden_id(self):
        """The orden_id attribute is accessible."""
        exc = OrdenNotFoundError(orden_id=42)
        assert exc.orden_id == 42


class TestInvalidOrdenDataError:
    """InvalidOrdenDataError carries a structured field + message."""

    def test_inherits_from_domain_error(self):
        """InvalidOrdenDataError inherits from DomainError."""
        assert issubclass(InvalidOrdenDataError, DomainError)

    def test_str_formats_field_and_message(self):
        """str(e) formats 'field message'."""
        exc = InvalidOrdenDataError(field="items", message="are required.")
        assert str(exc) == "items are required."

    def test_str_with_different_field(self):
        """str(e) works with different field names."""
        exc = InvalidOrdenDataError(field="cantidad", message="must be positive.")
        assert str(exc) == "cantidad must be positive."

    def test_preserves_field_and_message(self):
        """The field and message attributes are accessible."""
        exc = InvalidOrdenDataError(field="items", message="are required.")
        assert exc.field == "items"
        assert exc.message == "are required."


class TestInvalidEstadoTransitionError:
    """InvalidEstadoTransitionError carries actual and attempted estados."""

    def test_inherits_from_domain_error(self):
        """InvalidEstadoTransitionError inherits from DomainError."""
        assert issubclass(InvalidEstadoTransitionError, DomainError)

    def test_str_formats_actual_and_intentado(self):
        """str(e) formats the transition description."""
        exc = InvalidEstadoTransitionError(actual="entregado", intentado="preparando")
        assert str(exc) == "Cannot transition from entregado to preparando."

    def test_preserves_actual_and_intentado(self):
        """The actual and intentado attributes are accessible."""
        exc = InvalidEstadoTransitionError(actual="pendiente", intentado="pagado")
        assert exc.actual == "pendiente"
        assert exc.intentado == "pagado"
