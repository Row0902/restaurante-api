"""Tests for the MenuItem SQLModel.

Following Strict TDD: RED phase — test written before production code.
"""

from sqlmodel import SQLModel

from core.models.menu import MenuItem


class TestMenuItemModel:
    """MenuItem is a SQLModel table class for the menu_items table."""

    def test_inherits_from_sqlmodel(self):
        """MenuItem inherits from SQLModel with table=True."""
        assert issubclass(MenuItem, SQLModel)

    def test_tablename_is_menu_items(self):
        """__tablename__ equals 'menu_items'."""
        assert MenuItem.__tablename__ == "menu_items"

    def test_instantiation_with_required_fields(self):
        """MenuItem can be created with nombre and precio."""
        item = MenuItem(nombre="Pasta", precio=12.5)
        assert item.nombre == "Pasta"
        assert item.precio == 12.5

    def test_id_defaults_to_none(self):
        """Id defaults to None when not persisted."""
        item = MenuItem(nombre="Pasta", precio=12.5)
        assert item.id is None

    def test_optional_fields_default_to_none(self):
        """Categoria and descripcion default to None."""
        item = MenuItem(nombre="Pasta", precio=12.5)
        assert item.categoria is None
        assert item.descripcion is None

    def test_table_config_is_table_true(self):
        """MenuItem has the table=True configuration from SQLModel."""
        assert hasattr(MenuItem, "__tablename__")
        assert hasattr(MenuItem, "__table__")

    def test_instantiation_with_all_fields(self):
        """MenuItem can be created with all fields."""
        item = MenuItem(
            id=1,
            nombre="Pizza",
            precio=15.0,
            categoria="Principal",
            descripcion="Pizza margherita",
        )
        assert item.id == 1
        assert item.nombre == "Pizza"
        assert item.precio == 15.0
        assert item.categoria == "Principal"
        assert item.descripcion == "Pizza margherita"
