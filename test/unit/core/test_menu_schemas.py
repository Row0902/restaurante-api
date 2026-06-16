"""Tests for Pydantic v2 schemas with polymorphic validation.

Following Strict TDD: RED phase — test written before production code.
"""

import pytest

from core.exceptions import InvalidMenuDataError
from core.models.menu import MenuItem
from core.schemas.menu import PlatoCreate, PlatoResponse, PlatoUpdate


class TestPlatoCreateValidation:
    """PlatoCreate validates nombre and precio on creation."""

    def test_rejects_empty_nombre(self):
        """PlatoCreate.validate() raises InvalidMenuDataError when nombre is empty."""
        schema = PlatoCreate(nombre="", precio=10.0)
        with pytest.raises(InvalidMenuDataError) as excinfo:
            schema.validate()
        assert "nombre" in str(excinfo.value)

    def test_rejects_zero_precio(self):
        """PlatoCreate.validate() raises when precio is 0."""
        schema = PlatoCreate(nombre="Pasta", precio=0.0)
        with pytest.raises(InvalidMenuDataError) as excinfo:
            schema.validate()
        assert "precio" in str(excinfo.value)

    def test_rejects_negative_precio(self):
        """PlatoCreate.validate() raises when precio is negative."""
        schema = PlatoCreate(nombre="Pasta", precio=-5.0)
        with pytest.raises(InvalidMenuDataError) as excinfo:
            schema.validate()
        assert "precio" in str(excinfo.value)

    def test_accepts_valid_data(self):
        """PlatoCreate.validate() passes with valid nombre and precio."""
        schema = PlatoCreate(nombre="Pasta", precio=12.5)
        # Should not raise
        schema.validate()

    def test_optional_fields_default_to_none(self):
        """Categoria and descripcion default to None."""
        schema = PlatoCreate(nombre="Pasta", precio=12.5)
        assert schema.categoria is None
        assert schema.descripcion is None


class TestPlatoUpdateValidation:
    """PlatoUpdate validates only provided fields."""

    def test_rejects_empty_nombre_when_provided(self):
        """PlatoUpdate.validate() raises when nombre is explicitly empty."""
        schema = PlatoUpdate(nombre="")
        with pytest.raises(InvalidMenuDataError) as excinfo:
            schema.validate()
        assert "nombre" in str(excinfo.value)

    def test_rejects_negative_precio_when_provided(self):
        """PlatoUpdate.validate() raises when precio is explicitly negative."""
        schema = PlatoUpdate(precio=-5.0)
        with pytest.raises(InvalidMenuDataError) as excinfo:
            schema.validate()
        assert "precio" in str(excinfo.value)

    def test_accepts_empty_payload(self):
        """PlatoUpdate.validate() passes when no fields are set."""
        schema = PlatoUpdate()
        # Should not raise
        schema.validate()

    def test_accepts_partial_valid_payload(self):
        """PlatoUpdate.validate() passes with a single valid field."""
        schema = PlatoUpdate(nombre="New Name")
        # Should not raise
        schema.validate()

    def test_all_fields_default_to_none(self):
        """All PlatoUpdate fields default to None."""
        schema = PlatoUpdate()
        assert schema.nombre is None
        assert schema.precio is None
        assert schema.categoria is None
        assert schema.descripcion is None


class TestPlatoResponse:
    """PlatoResponse serializes MenuItem instances via from_attributes."""

    def test_from_attributes_with_minimal_data(self):
        """PlatoResponse can be built from a MenuItem with minimal fields."""
        item = MenuItem(id=1, nombre="Pasta", precio=12.5)
        response = PlatoResponse.model_validate(item)
        assert response.id == 1
        assert response.nombre == "Pasta"
        assert response.precio == 12.5
        assert response.categoria is None
        assert response.descripcion is None

    def test_from_attributes_with_all_fields(self):
        """PlatoResponse includes all fields when built from MenuItem."""
        item = MenuItem(
            id=2,
            nombre="Pizza",
            precio=15.0,
            categoria="Principal",
            descripcion="Pizza margherita",
        )
        response = PlatoResponse.model_validate(item)
        assert response.id == 2
        assert response.nombre == "Pizza"
        assert response.precio == 15.0
        assert response.categoria == "Principal"
        assert response.descripcion == "Pizza margherita"

    def test_serialization_to_dict(self):
        """PlatoResponse model_dump() produces expected dict."""
        item = MenuItem(id=1, nombre="Pasta", precio=12.5)
        response = PlatoResponse.model_validate(item)
        data = response.model_dump()
        assert data == {
            "id": 1,
            "nombre": "Pasta",
            "precio": 12.5,
            "categoria": None,
            "descripcion": None,
        }
