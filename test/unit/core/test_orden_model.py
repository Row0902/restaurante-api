"""Tests for the Orden and OrdenItem SQLModel models.

Following Strict TDD: RED phase — test written before production code.
"""

from datetime import datetime

from sqlmodel import SQLModel

from core.models.orden import Orden, OrdenItem


class TestOrdenItemModel:
    """OrdenItem is a SQLModel table class for orden_items."""

    def test_inherits_from_sqlmodel(self):
        """OrdenItem inherits from SQLModel with table=True."""
        assert issubclass(OrdenItem, SQLModel)

    def test_tablename_is_orden_items(self):
        """__tablename__ equals 'orden_items'."""
        assert OrdenItem.__tablename__ == "orden_items"

    def test_instantiation_with_required_fields(self):
        """OrdenItem can be created with required fields."""
        item = OrdenItem(
            orden_id=1, plato_id=1, cantidad=2, precio_unitario=12.5, nombre="Pasta"
        )
        assert item.plato_id == 1
        assert item.cantidad == 2
        assert item.precio_unitario == 12.5
        assert item.nombre == "Pasta"

    def test_id_defaults_to_none(self):
        """Id defaults to None when not persisted."""
        item = OrdenItem(
            orden_id=1, plato_id=1, cantidad=2, precio_unitario=12.5, nombre="Pasta"
        )
        assert item.id is None

    def test_precio_unitario_is_snapshot(self):
        """precio_unitario preserves the frozen value."""
        item = OrdenItem(
            orden_id=1, plato_id=1, cantidad=2, precio_unitario=12.5, nombre="Pasta"
        )
        assert item.precio_unitario == 12.5


class TestOrdenModel:
    """Orden is a SQLModel table class for ordenes."""

    def test_inherits_from_sqlmodel(self):
        """Orden inherits from SQLModel with table=True."""
        assert issubclass(Orden, SQLModel)

    def test_tablename_is_ordenes(self):
        """__tablename__ equals 'ordenes'."""
        assert Orden.__tablename__ == "ordenes"

    def test_instantiation_with_required_fields(self):
        """Orden can be created with total."""
        orden = Orden(total=25.0)
        assert orden.total == 25.0

    def test_id_defaults_to_none(self):
        """Id defaults to None when not persisted."""
        orden = Orden(total=25.0)
        assert orden.id is None

    def test_estado_defaults_to_pendiente(self):
        """Estado defaults to 'pendiente'."""
        orden = Orden(total=25.0)
        assert orden.estado == "pendiente"

    def test_mesa_defaults_to_none(self):
        """Mesa defaults to None."""
        orden = Orden(total=25.0)
        assert orden.mesa is None

    def test_created_at_defaults_to_datetime_now(self):
        """Created_at defaults to datetime.now() when not provided."""
        orden = Orden(total=25.0)
        assert orden.created_at is not None
        assert isinstance(orden.created_at, datetime)

    def test_created_at_can_be_none(self):
        """Created_at can be set to None explicitly."""
        orden = Orden(total=25.0, created_at=None)
        assert orden.created_at is None

    def test_instantiation_with_all_fields(self):
        """Orden can be created with all fields."""
        orden = Orden(
            id=1,
            total=35.0,
            estado="preparando",
            mesa=5,
            created_at=datetime(2026, 6, 16, 10, 0, 0),
        )
        assert orden.id == 1
        assert orden.total == 35.0
        assert orden.estado == "preparando"
        assert orden.mesa == 5
        assert orden.created_at == datetime(2026, 6, 16, 10, 0, 0)

    def test_items_relationship_defaults_to_empty(self):
        """Items relationship defaults to empty list."""
        orden = Orden(total=25.0)
        assert orden.items == []
