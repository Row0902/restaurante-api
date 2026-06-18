"""Tests para la interfaz abstracta de OrderRepository.

Verifica que el ABC define los métodos requeridos (R7).
"""

import pytest

from core.enums.order_status import OrderStatus
from core.models.order import Order
from core.repositories.ordenes import AbstractOrderRepository


class TestAbstractOrderRepository:
    def test_abc_no_se_puede_instanciar(self):
        with pytest.raises(TypeError):
            AbstractOrderRepository()  # type: ignore[abstract]

    def test_subclase_incompleta_explota(self):
        class Incompleta(AbstractOrderRepository):
            pass

        with pytest.raises(TypeError):
            Incompleta()  # type: ignore[abstract]

    def test_subclase_completa_es_valida(self):
        class Completa(AbstractOrderRepository):
            async def get_all(self) -> list[Order]:
                return []

            async def get_by_id(self, order_id: int) -> Order:
                raise NotImplementedError

            async def add(self, order: Order) -> Order:
                return order

            async def update_estado(self, order_id: int, estado: OrderStatus) -> Order:
                raise NotImplementedError

        inst = Completa()
        assert isinstance(inst, AbstractOrderRepository)
