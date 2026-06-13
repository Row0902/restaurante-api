"""Tests unitarios para el valor de dominio Cantidad."""

import pytest

from core.cantidad import Cantidad
from core.dominio_error import DominioError


def test_cantidad_acepta_enteros_positivos():
    """Verifica que Cantidad conserve enteros positivos."""
    assert Cantidad(3).valor == 3


@pytest.mark.parametrize("valor", [0, -1])
def test_cantidad_rechaza_cero_y_negativos(valor):
    """Verifica que Cantidad rechace valores no positivos."""
    with pytest.raises(DominioError, match="cantidad debe ser mayor que cero"):
        Cantidad(valor)


@pytest.mark.parametrize("valor", ["2", 1.5])
def test_cantidad_rechaza_valores_no_enteros(valor):
    """Verifica que Cantidad rechace valores que no son enteros."""
    with pytest.raises(DominioError, match="cantidad debe ser un entero"):
        Cantidad(valor)
