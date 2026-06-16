"""Unit tests for Orden and OrdenItem SQLModels."""

import pytest
from pydantic import ValidationError

from core.models import Orden, OrdenItem


def test_orden_creation_with_defaults() -> None:
    """Verify Orden defaults: estado='pendiente', total=0.0."""
    orden = Orden()
    assert orden.estado == "pendiente"
    assert orden.total == 0.0


def test_orden_items_storage() -> None:
    """Verify Orden stores OrdenItem list correctly."""
    item = OrdenItem(plato_id=1, cantidad=2)
    orden = Orden(items=[item])
    assert len(orden.items) == 1
    assert orden.items[0].plato_id == 1
    assert orden.items[0].cantidad == 2


def test_orden_item_cantidad_minimum() -> None:
    """Verify OrdenItem rejects cantidad < 1."""
    with pytest.raises(ValidationError):
        OrdenItem(plato_id=1, cantidad=0)
