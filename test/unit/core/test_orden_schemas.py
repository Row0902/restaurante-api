"""Tests for Pydantic v2 schemas with polymorphic validation.

Following Strict TDD: RED phase — test written before production code.
"""

from datetime import datetime

import pytest

from core.exceptions import InvalidOrdenDataError
from core.models.orden import Orden, OrdenItem
from core.schemas.orden import (
    OrdenCreate,
    OrdenItemData,
    OrdenResponse,
    OrdenUpdateEstado,
)


class TestOrdenItemData:
    """OrdenItemData validates plato_id and cantidad on creation."""

    def test_rejects_zero_plato_id(self):
        """OrdenItemData.validate() raises when plato_id is 0."""
        schema = OrdenItemData(plato_id=0, cantidad=2)
        with pytest.raises(InvalidOrdenDataError) as excinfo:
            schema.validate()
        assert "plato_id" in str(excinfo.value)

    def test_rejects_zero_cantidad(self):
        """OrdenItemData.validate() raises when cantidad is 0."""
        schema = OrdenItemData(plato_id=1, cantidad=0)
        with pytest.raises(InvalidOrdenDataError) as excinfo:
            schema.validate()
        assert "cantidad" in str(excinfo.value)

    def test_rejects_negative_cantidad(self):
        """OrdenItemData.validate() raises when cantidad is negative."""
        schema = OrdenItemData(plato_id=1, cantidad=-3)
        with pytest.raises(InvalidOrdenDataError) as excinfo:
            schema.validate()
        assert "cantidad" in str(excinfo.value)

    def test_accepts_valid_data(self):
        """OrdenItemData.validate() passes with valid plato_id and cantidad."""
        schema = OrdenItemData(plato_id=1, cantidad=2)
        schema.validate()  # Should not raise


class TestOrdenCreate:
    """OrdenCreate validates items list and delegates to items."""

    def test_rejects_empty_items(self):
        """OrdenCreate.validate() raises when items list is empty."""
        schema = OrdenCreate(items=[])
        with pytest.raises(InvalidOrdenDataError) as excinfo:
            schema.validate()
        assert "items" in str(excinfo.value)

    def test_accepts_valid_items(self):
        """OrdenCreate.validate() passes with valid non-empty items."""
        schema = OrdenCreate(items=[OrdenItemData(plato_id=1, cantidad=2)])
        schema.validate()  # Should not raise

    def test_mesa_defaults_to_none(self):
        """Mesa defaults to None when not provided."""
        schema = OrdenCreate(items=[OrdenItemData(plato_id=1, cantidad=2)])
        assert schema.mesa is None

    def test_validates_each_item(self):
        """OrdenCreate.validate() propagates item-level validation errors."""
        schema = OrdenCreate(items=[OrdenItemData(plato_id=1, cantidad=0)])
        with pytest.raises(InvalidOrdenDataError) as excinfo:
            schema.validate()
        assert "cantidad" in str(excinfo.value)

    def test_validates_multiple_items(self):
        """OrdenCreate accepts multiple valid items."""
        schema = OrdenCreate(
            items=[
                OrdenItemData(plato_id=1, cantidad=2),
                OrdenItemData(plato_id=3, cantidad=1),
            ],
            mesa=4,
        )
        schema.validate()  # Should not raise
        assert schema.mesa == 4


class TestOrdenUpdateEstado:
    """OrdenUpdateEstado validates estado field."""

    def test_rejects_invalid_estado(self):
        """OrdenUpdateEstado.validate() raises for unknown estado."""
        schema = OrdenUpdateEstado(estado="inexistente")
        with pytest.raises(InvalidOrdenDataError) as excinfo:
            schema.validate()
        assert "estado" in str(excinfo.value)

    def test_accepts_valid_estado_pendiente(self):
        """OrdenUpdateEstado accepts 'pendiente'."""
        schema = OrdenUpdateEstado(estado="pendiente")
        schema.validate()  # Should not raise

    def test_accepts_valid_estado_preparando(self):
        """OrdenUpdateEstado accepts 'preparando'."""
        schema = OrdenUpdateEstado(estado="preparando")
        schema.validate()  # Should not raise

    def test_accepts_valid_estado_entregado(self):
        """OrdenUpdateEstado accepts 'entregado'."""
        schema = OrdenUpdateEstado(estado="entregado")
        schema.validate()  # Should not raise

    def test_accepts_valid_estado_pagado(self):
        """OrdenUpdateEstado accepts 'pagado'."""
        schema = OrdenUpdateEstado(estado="pagado")
        schema.validate()  # Should not raise

    def test_accepts_valid_estado_cancelado(self):
        """OrdenUpdateEstado accepts 'cancelado'."""
        schema = OrdenUpdateEstado(estado="cancelado")
        schema.validate()  # Should not raise


class TestOrdenResponse:
    """OrdenResponse serializes Orden instances via from_attributes."""

    def test_from_attributes_with_minimal_data(self):
        """OrdenResponse can be built from an Orden with persisted fields."""
        orden = Orden(id=5, total=25.0)
        response = OrdenResponse.model_validate(orden)
        assert response.id == 5
        assert response.total == 25.0
        assert response.estado == "pendiente"
        assert response.mesa is None
        assert isinstance(response.created_at, datetime)

    def test_created_at_defaults_to_datetime_now(self):
        """OrdenResponse.created_at reflects the model default."""
        orden = Orden(id=5, total=25.0)
        response = OrdenResponse.model_validate(orden)
        assert response.created_at is not None

    def test_sets_id_from_model(self):
        """OrdenResponse includes the persisted id."""
        orden = Orden(id=5, total=25.0)
        response = OrdenResponse.model_validate(orden)
        assert response.id == 5

    def test_includes_items(self):
        """OrdenResponse includes items as a list."""
        item = OrdenItem(
            id=1,
            orden_id=1,
            plato_id=1,
            cantidad=2,
            precio_unitario=12.5,
            nombre="Pasta",
        )
        orden = Orden(id=1, total=25.0, items=[item])
        response = OrdenResponse.model_validate(orden)
        assert len(response.items) == 1
        assert response.items[0].id == 1
        assert response.items[0].plato_id == 1
        assert response.items[0].cantidad == 2
        assert response.items[0].precio_unitario == 12.5
        assert response.items[0].nombre == "Pasta"

    def test_model_dump_serialization(self):
        """OrdenResponse.model_dump() produces expected dict."""
        item = OrdenItem(
            id=1,
            orden_id=1,
            plato_id=1,
            cantidad=2,
            precio_unitario=12.5,
            nombre="Pasta",
        )
        orden = Orden(id=1, total=25.0, estado="pendiente", items=[item])
        response = OrdenResponse.model_validate(orden)
        data = response.model_dump()
        assert data["id"] == 1
        assert data["total"] == 25.0
        assert data["estado"] == "pendiente"
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == 1
        assert data["items"][0]["plato_id"] == 1
