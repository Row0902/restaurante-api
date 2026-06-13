"""Tests unitarios para Plato."""

import pytest

from core.dominio_error import DominioError
from core.plato import Plato
from core.precio import Precio


def test_plato_conserva_identidad_nombre_y_precio():
    """Verifica datos basicos de un plato valido."""
    precio = Precio("12.50")

    plato = Plato(id="1", nombre="Pizza", precio=precio)

    assert plato.id == "1"
    assert plato.nombre == "Pizza"
    assert plato.precio == precio


@pytest.mark.parametrize("id_plato", ["", "   "])
def test_plato_rechaza_id_vacio(id_plato):
    """Verifica que Plato requiera identidad."""
    with pytest.raises(DominioError, match="id de plato requerido"):
        Plato(id=id_plato, nombre="Pizza", precio=Precio("10"))


@pytest.mark.parametrize("nombre", ["", "   "])
def test_plato_rechaza_nombre_vacio(nombre):
    """Verifica que Plato requiera nombre."""
    with pytest.raises(DominioError, match="nombre de plato requerido"):
        Plato(id="1", nombre=nombre, precio=Precio("10"))
