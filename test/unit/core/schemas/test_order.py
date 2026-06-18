"""Tests para los schemas de órdenes (Pydantic DTOs)."""

import pytest
from pydantic import ValidationError

from core.enums.order_status import OrderStatus
from core.schemas.order import (
    CreateOrdenItemRequest,
    CreateOrdenRequest,
    EstadoUpdateRequest,
    OrdenResponse,
)


class TestCreateOrdenItemRequest:
    def test_valido(self):
        item = CreateOrdenItemRequest(plato_id=1, cantidad=2)
        assert item.plato_id == 1
        assert item.cantidad == 2

    def test_cantidad_default_uno(self):
        item = CreateOrdenItemRequest(plato_id=1)
        assert item.cantidad == 1

    def test_plato_id_requerido(self):
        with pytest.raises(ValidationError):
            CreateOrdenItemRequest(cantidad=2)  # type: ignore[call-arg]

    def test_plato_id_positivo(self):
        with pytest.raises(ValidationError):
            CreateOrdenItemRequest(plato_id=0, cantidad=1)

    def test_cantidad_minima_uno(self):
        with pytest.raises(ValidationError):
            CreateOrdenItemRequest(plato_id=1, cantidad=0)


class TestCreateOrdenRequest:
    def test_valido_un_item(self):
        req = CreateOrdenRequest(items=[CreateOrdenItemRequest(plato_id=1, cantidad=2)])
        assert len(req.items) == 1

    def test_valido_varios_items(self):
        req = CreateOrdenRequest(
            items=[
                CreateOrdenItemRequest(plato_id=1, cantidad=2),
                CreateOrdenItemRequest(plato_id=2, cantidad=1),
            ]
        )
        assert len(req.items) == 2

    def test_items_no_vacio(self):
        with pytest.raises(ValidationError):
            CreateOrdenRequest(items=[])


class TestEstadoUpdateRequest:
    def test_estado_valido(self):
        req = EstadoUpdateRequest(estado=OrderStatus.entregado)
        assert req.estado == OrderStatus.entregado

    def test_estado_desde_string(self):
        req = EstadoUpdateRequest(estado="pendiente")
        assert req.estado == OrderStatus.pendiente

    def test_estado_invalido(self):
        with pytest.raises(ValidationError):
            EstadoUpdateRequest(estado="inexistente")


class TestOrdenResponse:
    def test_crear_respuesta(self):
        response = OrdenResponse(id=1, total=25.0, estado="pendiente", items=[])
        assert response.id == 1
        assert response.total == 25.0
        assert response.estado == "pendiente"
