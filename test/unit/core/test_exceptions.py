"""Tests para las excepciones de dominio.

Regla R15: excepciones de dominio propias con mensaje descriptivo.
"""

from core.exceptions.base import AppBaseError
from core.exceptions.duplicate import MenuItemDuplicateError
from core.exceptions.invalid_state import InvalidOrderStateError
from core.exceptions.not_found import (
    MenuItemNotFoundError,
    OrderNotFoundError,
)


class TestAppBaseError:
    """La excepción base debe tener mensaje y código."""

    def test_tiene_mensaje(self):
        exc = AppBaseError("Algo salió mal")
        assert str(exc) == "Algo salió mal"

    def test_tiene_codigo_por_defecto(self):
        exc = AppBaseError("Error")
        assert exc.codigo == "ERROR"

    def test_codigo_personalizado(self):
        exc = AppBaseError("No encontrado", codigo="NOT_FOUND")
        assert exc.codigo == "NOT_FOUND"


class TestMenuItemNotFoundError:
    def test_hereda_de_app_base_exception(self):
        exc = MenuItemNotFoundError(plato_id=42)
        assert isinstance(exc, AppBaseError)

    def test_mensaje_incluye_id(self):
        exc = MenuItemNotFoundError(plato_id=42)
        assert "42" in str(exc)
        assert "plato" in str(exc).lower()

    def test_tiene_codigo(self):
        exc = MenuItemNotFoundError(plato_id=1)
        assert exc.codigo == "MENU_ITEM_NOT_FOUND"


class TestOrderNotFoundError:
    def test_hereda_de_app_base_exception(self):
        exc = OrderNotFoundError(orden_id=99)
        assert isinstance(exc, AppBaseError)

    def test_mensaje_incluye_id(self):
        exc = OrderNotFoundError(orden_id=99)
        assert "99" in str(exc)
        assert "orden" in str(exc).lower()

    def test_tiene_codigo(self):
        exc = OrderNotFoundError(orden_id=1)
        assert exc.codigo == "ORDER_NOT_FOUND"


class TestMenuItemDuplicateError:
    def test_hereda_de_app_base_exception(self):
        exc = MenuItemDuplicateError(nombre="Pizza")
        assert isinstance(exc, AppBaseError)

    def test_mensaje_incluye_nombre(self):
        exc = MenuItemDuplicateError(nombre="Pizza")
        assert "Pizza" in str(exc)
        assert "existe" in str(exc).lower()

    def test_tiene_codigo(self):
        exc = MenuItemDuplicateError(nombre="Pizza")
        assert exc.codigo == "MENU_ITEM_DUPLICATE"


class TestInvalidOrderStateError:
    def test_hereda_de_app_base_exception(self):
        exc = InvalidOrderStateError(
            actual="pendiente",
            destino="entregado",
        )
        assert isinstance(exc, AppBaseError)

    def test_mensaje_incluye_estados(self):
        exc = InvalidOrderStateError(
            actual="pendiente",
            destino="entregado",
        )
        assert "pendiente" in str(exc)
        assert "entregado" in str(exc)

    def test_tiene_codigo(self):
        exc = InvalidOrderStateError(actual="a", destino="b")
        assert exc.codigo == "INVALID_ORDER_STATE"
