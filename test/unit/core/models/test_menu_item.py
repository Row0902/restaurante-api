"""Tests para la entidad MenuItem."""

from core.models.menu_item import MenuItem


class TestMenuItem:
    def test_crear_con_campos_obligatorios(self):
        item = MenuItem(nombre="Pizza", precio=12.5)
        assert item.nombre == "Pizza"
        assert item.precio == 12.5

    def test_crear_con_campos_extra(self):
        item = MenuItem(
            nombre="Pizza", precio=12.5, categoria="Principal", descripcion="Margherita"
        )
        assert item.categoria == "Principal"
        assert item.descripcion == "Margherita"

    def test_id_es_none_por_defecto(self):
        item = MenuItem(nombre="Pizza", precio=12.5)
        assert item.id is None

    def test_es_subclase_de_sqlmodel(self):
        from sqlmodel import SQLModel

        item = MenuItem(nombre="Pizza", precio=12.5)
        assert isinstance(item, SQLModel)

    def test_tabla_nombre(self):
        assert MenuItem.__tablename__ == "menu_item"
