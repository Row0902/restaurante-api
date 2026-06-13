"""Tests unitarios para el valor de dominio Precio."""

from decimal import Decimal

import pytest

from core.dominio_error import DominioError
from core.precio import Precio


def test_precio_acepta_cero_y_decimales():
    """Verifica que Precio normalice montos validos a Decimal."""
    assert Precio(0).monto == Decimal("0")
    assert Precio("10.50").monto == Decimal("10.50")


def test_precio_rechaza_montos_negativos():
    """Verifica que Precio rechace valores negativos."""
    with pytest.raises(DominioError, match="precio no puede ser negativo"):
        Precio(Decimal("-0.01"))


def test_precio_rechaza_montos_no_numericos():
    """Verifica que Precio rechace valores que no representan dinero."""
    with pytest.raises(DominioError, match="precio invalido"):
        Precio("caro")


def test_precio_suma_otro_precio():
    """Verifica suma de precios como value object."""
    assert Precio("10.25").sumar(Precio("2.75")) == Precio("13.00")
