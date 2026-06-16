"""Unit tests for Plato SQLModel."""

from core.models import Plato


def test_plato_creation_with_valid_data() -> None:
    """Verify Plato creation with all fields populated."""
    plato = Plato(
        id=1,
        nombre="Milanesa",
        precio=1500.0,
        descripcion="Milanesa de ternera con pure",
        disponible=True,
    )
    assert plato.id == 1
    assert plato.nombre == "Milanesa"
    assert plato.precio == 1500.0
    assert plato.descripcion == "Milanesa de ternera con pure"
    assert plato.disponible is True


def test_plato_creation_minimal() -> None:
    """Verify Plato creation with only required fields."""
    plato = Plato(nombre="Ensalada", precio=800.0)
    assert plato.nombre == "Ensalada"
    assert plato.precio == 800.0


def test_plato_precio_can_be_zero() -> None:
    """Verify Plato accepts zero as valid precio (lower bound)."""
    plato = Plato(nombre="Test", precio=0.0)
    assert plato.precio == 0.0


def test_plato_default_values() -> None:
    """Verify Plato defaults: disponible=True, descripcion=None."""
    plato = Plato(nombre="Test", precio=500.0)
    assert plato.disponible is True
    assert plato.descripcion is None


def test_plato_id_is_none_before_persist() -> None:
    """Verify Plato id is None before database persistence."""
    plato = Plato(nombre="Test", precio=500.0)
    assert plato.id is None
