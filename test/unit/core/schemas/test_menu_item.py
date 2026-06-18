"""Tests para los schemas de menú (Pydantic DTOs)."""

import pytest
from pydantic import ValidationError

from core.schemas.menu_item import CreatePlatoRequest, PlatoResponse


class TestCreatePlatoRequest:
    def test_valido_con_campos_minimos(self):
        schema = CreatePlatoRequest(nombre="Pizza", precio=12.5)
        assert schema.nombre == "Pizza"
        assert schema.precio == 12.5

    def test_valido_con_campos_extra(self):
        schema = CreatePlatoRequest(
            nombre="Pizza",
            precio=12.5,
            categoria="Principal",
            descripcion="Margherita",
        )
        assert schema.categoria == "Principal"

    def test_nombre_requerido(self):
        with pytest.raises(ValidationError):
            CreatePlatoRequest(precio=12.5)  # type: ignore[call-arg]

    def test_precio_requerido(self):
        with pytest.raises(ValidationError):
            CreatePlatoRequest(nombre="Pizza")  # type: ignore[call-arg]

    def test_precio_debe_ser_positivo(self):
        with pytest.raises(ValidationError):
            CreatePlatoRequest(nombre="Pizza", precio=-5.0)

    def test_nombre_no_vacio(self):
        with pytest.raises(ValidationError):
            CreatePlatoRequest(nombre="", precio=10.0)


class TestPlatoResponse:
    def test_crear_desde_datos(self):
        response = PlatoResponse(
            id=1, nombre="Pizza", precio=12.5, categoria="Principal"
        )
        assert response.id == 1
        assert response.nombre == "Pizza"

    def test_campos_opcionales_ausentes(self):
        response = PlatoResponse(id=1, nombre="Pizza", precio=12.5)
        assert response.categoria is None
        assert response.descripcion is None
