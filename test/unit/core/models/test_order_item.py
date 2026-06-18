"""Tests para la entidad OrderItem."""

from core.models.order_item import OrderItem


class TestOrderItem:
    def test_crear_order_item(self):
        item = OrderItem(menu_item_id=1, cantidad=2, precio_unitario=12.5)
        assert item.menu_item_id == 1
        assert item.cantidad == 2
        assert item.precio_unitario == 12.5

    def test_id_es_none_por_defecto(self):
        item = OrderItem(menu_item_id=1, cantidad=1, precio_unitario=10.0)
        assert item.id is None

    def test_es_subclase_de_sqlmodel(self):
        from sqlmodel import SQLModel

        item = OrderItem(menu_item_id=1, cantidad=1, precio_unitario=10.0)
        assert isinstance(item, SQLModel)

    def test_tabla_nombre(self):
        assert OrderItem.__tablename__ == "order_item"
