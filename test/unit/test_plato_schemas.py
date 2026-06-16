"""Unit tests for Plato Pydantic schemas."""

import pytest
from pydantic import ValidationError

from core.models import Plato
from core.schemas import PlatoCreate, PlatoResponse, PlatoUpdate


def test_plato_create_valid() -> None:
    """Verify PlatoCreate accepts valid data."""
    schema = PlatoCreate(
        nombre="Milanesa",
        precio=1500.0,
        descripcion="Con pure",
        disponible=True,
    )
    assert schema.nombre == "Milanesa"
    assert schema.precio == 1500.0
    assert schema.descripcion == "Con pure"
    assert schema.disponible is True


def test_plato_create_missing_nombre() -> None:
    """Verify PlatoCreate rejects missing nombre."""
    with pytest.raises(ValidationError):
        PlatoCreate(precio=1500.0)  # ty: ignore[missing-argument]


def test_plato_create_zero_precio() -> None:
    """Verify PlatoCreate rejects precio=0 (gt=0)."""
    with pytest.raises(ValidationError):
        PlatoCreate(nombre="Test", precio=0.0)


def test_plato_create_negative_precio() -> None:
    """Verify PlatoCreate rejects negative precio."""
    with pytest.raises(ValidationError):
        PlatoCreate(nombre="Test", precio=-100.0)


def test_plato_update_all_none() -> None:
    """Verify PlatoUpdate has all fields optional."""
    update = PlatoUpdate()
    assert update.nombre is None
    assert update.precio is None
    assert update.descripcion is None
    assert update.disponible is None


def test_plato_update_partial() -> None:
    """Verify PlatoUpdate accepts partial data."""
    update = PlatoUpdate(nombre="Nuevo nombre")
    assert update.nombre == "Nuevo nombre"
    assert update.precio is None


def test_plato_response_serialization() -> None:
    """Verify PlatoResponse can be built from a Plato model instance."""
    plato = Plato(
        id=1,
        nombre="Milanesa",
        precio=1500.0,
        descripcion="Con pure",
        disponible=True,
    )
    response = PlatoResponse.model_validate(plato)
    assert response.id == 1
    assert response.nombre == "Milanesa"
    assert response.precio == 1500.0
    assert response.descripcion == "Con pure"
    assert response.disponible is True
