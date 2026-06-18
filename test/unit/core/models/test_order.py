"""Tests para la entidad Order."""

from core.enums.order_status import OrderStatus
from core.models.order import Order


class TestOrder:
    def test_crear_orden_basica(self):
        orden = Order()
        assert orden.estado == OrderStatus.pendiente

    def test_estado_default_es_pendiente(self):
        orden = Order()
        assert orden.estado == OrderStatus.pendiente
        assert orden.estado == "pendiente"

    def test_total_default_es_cero(self):
        orden = Order()
        assert orden.total == 0.0

    def test_id_es_none_por_defecto(self):
        orden = Order()
        assert orden.id is None

    def test_es_subclase_de_sqlmodel(self):
        from sqlmodel import SQLModel

        orden = Order()
        assert isinstance(orden, SQLModel)

    def test_tabla_nombre(self):
        assert Order.__tablename__ == "order"
