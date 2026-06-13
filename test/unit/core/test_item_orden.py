"""Tests unitarios para ItemOrden."""

import pytest

from core.cantidad import Cantidad
from core.dominio_error import DominioError
from core.item_orden import ItemOrden
from core.precio import Precio


def test_item_orden_calcula_subtotal():
    """Verifica subtotal segun precio unitario y cantidad."""
    item = ItemOrden(
        plato_id="1",
        cantidad=Cantidad(3),
        precio_unitario=Precio("7.50"),
    )

    assert item.subtotal() == Precio("22.50")


@pytest.mark.parametrize("plato_id", ["", "   "])
def test_item_orden_rechaza_plato_id_vacio(plato_id):
    """Verifica que ItemOrden requiera referencia a plato."""
    with pytest.raises(DominioError, match="id de plato requerido"):
        ItemOrden(
            plato_id=plato_id,
            cantidad=Cantidad(1),
            precio_unitario=Precio("5"),
        )
