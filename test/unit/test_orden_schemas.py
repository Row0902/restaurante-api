"""Unit tests for Orden Pydantic schemas."""

import pytest
from pydantic import ValidationError

from core.schemas import (
    EstadoUpdate,
    OrdenCreate,
    OrdenItemSchema,
    OrdenResponse,
)


def test_orden_create_valid() -> None:
    """Verify OrdenCreate accepts valid items list."""
    schema = OrdenCreate(items=[OrdenItemSchema(plato_id=1, cantidad=2)])
    assert len(schema.items) == 1
    assert schema.items[0].plato_id == 1
    assert schema.items[0].cantidad == 2


def test_orden_create_empty_items() -> None:
    """Verify OrdenCreate rejects empty items list."""
    with pytest.raises(ValidationError):
        OrdenCreate(items=[])


def test_orden_create_zero_cantidad() -> None:
    """Verify OrdenItemSchema rejects cantidad=0."""
    with pytest.raises(ValidationError):
        OrdenItemSchema(plato_id=1, cantidad=0)


def test_orden_response_serialization() -> None:
    """Verify OrdenResponse round-trip serialization."""
    response = OrdenResponse(
        id=1,
        items=[OrdenItemSchema(plato_id=1, cantidad=2)],
        total=3000.0,
        estado="pendiente",
    )
    assert response.id == 1
    assert response.total == 3000.0
    assert response.estado == "pendiente"
    assert len(response.items) == 1


def test_estado_update_valid() -> None:
    """Verify EstadoUpdate accepts valid estado string."""
    schema = EstadoUpdate(estado="entregado")
    assert schema.estado == "entregado"


def test_estado_update_empty() -> None:
    """Verify EstadoUpdate rejects empty string."""
    with pytest.raises(ValidationError):
        EstadoUpdate(estado="")
