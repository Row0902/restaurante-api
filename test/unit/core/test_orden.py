"""Tests unitarios para Orden."""

import pytest

from core.cantidad import Cantidad
from core.dominio_error import DominioError
from core.estado_orden import EstadoOrden
from core.item_orden import ItemOrden
from core.orden import Orden
from core.precio import Precio


def test_orden_nace_pendiente_y_calcula_total():
    """Verifica estado inicial y total calculado desde items."""
    orden = Orden(id="1", items=(item("1", 2, "10"), item("2", 1, "3.50")))

    assert orden.estado == EstadoOrden.PENDIENTE
    assert orden.total() == Precio("23.50")


def test_orden_sin_items_tiene_total_cero():
    """Verifica total de una orden vacia."""
    assert Orden(id="1", items=()).total() == Precio("0")


def test_orden_cambia_a_estado_valido_sin_mutar_original():
    """Verifica cambio de estado como nueva instancia."""
    orden = Orden(id="1", items=())

    actualizada = orden.cambiar_estado(EstadoOrden.EN_PREPARACION)

    assert orden.estado == EstadoOrden.PENDIENTE
    assert actualizada.estado == EstadoOrden.EN_PREPARACION


def test_orden_rechaza_transicion_invalida():
    """Verifica que Orden respete reglas de EstadoOrden."""
    orden = Orden(id="1", items=())

    with pytest.raises(DominioError, match="transicion de estado invalida"):
        orden.cambiar_estado(EstadoOrden.ENTREGADA)


@pytest.mark.parametrize("orden_id", ["", "   "])
def test_orden_rechaza_id_vacio(orden_id):
    """Verifica que Orden requiera identidad."""
    with pytest.raises(DominioError, match="id de orden requerido"):
        Orden(id=orden_id, items=())


def item(plato_id: str, cantidad: int, precio: str) -> ItemOrden:
    """Crea un item de orden para pruebas."""
    return ItemOrden(
        plato_id=plato_id,
        cantidad=Cantidad(cantidad),
        precio_unitario=Precio(precio),
    )
