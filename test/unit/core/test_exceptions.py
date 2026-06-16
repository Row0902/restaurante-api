"""Tests for the domain exception hierarchy.

Following Strict TDD: RED phase — test written before production code.
"""

from core.exceptions import DomainError, InvalidMenuDataError, MenuNotFoundError


class TestDomainErrorHierarchy:
    """DomainError is the base class for all domain exceptions."""

    def test_domain_error_is_base(self):
        """DomainError inherits from Exception."""
        assert issubclass(DomainError, Exception)

    def test_menu_not_found_error_inherits_domain_error(self):
        """MenuNotFoundError inherits from DomainError."""
        assert issubclass(MenuNotFoundError, DomainError)

    def test_invalid_menu_data_error_inherits_domain_error(self):
        """InvalidMenuDataError inherits from DomainError."""
        assert issubclass(InvalidMenuDataError, DomainError)


class TestMenuNotFoundError:
    """MenuNotFoundError carries a descriptive message formatted from plato_id."""

    def test_str_with_integer_id(self):
        """str(e) formats plato_id as int."""
        exc = MenuNotFoundError(plato_id=99)
        assert str(exc) == "Menu item 99 not found."

    def test_str_with_string_id(self):
        """str(e) formats plato_id as str."""
        exc = MenuNotFoundError(plato_id="abc")
        assert str(exc) == "Menu item abc not found."

    def test_preserves_plato_id(self):
        """The plato_id attribute is accessible."""
        exc = MenuNotFoundError(plato_id=42)
        assert exc.plato_id == 42


class TestInvalidMenuDataError:
    """InvalidMenuDataError carries a structured field + message."""

    def test_str_formats_field_and_message(self):
        """str(e) formats 'field message'."""
        exc = InvalidMenuDataError(field="precio", message="must be positive.")
        assert str(exc) == "precio must be positive."

    def test_str_with_different_field(self):
        """str(e) works with different field names."""
        exc = InvalidMenuDataError(field="nombre", message="is required.")
        assert str(exc) == "nombre is required."

    def test_preserves_field_and_message(self):
        """The field and message attributes are accessible."""
        exc = InvalidMenuDataError(field="precio", message="must be positive.")
        assert exc.field == "precio"
        assert exc.message == "must be positive."
