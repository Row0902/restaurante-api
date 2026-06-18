"""Tests para la interfaz abstracta de MenuRepository.

Verifica que el ABC define los métodos requeridos (R7).
"""

import pytest

from core.models.menu_item import MenuItem
from core.repositories.menu import AbstractMenuRepository


class TestAbstractMenuRepository:
    def test_abc_no_se_puede_instanciar(self):
        with pytest.raises(TypeError):
            AbstractMenuRepository()  # type: ignore[abstract]

    def test_subclase_concreta_sin_metodos_explota(self):
        """Una subclase sin implementar todos los abstractmethods falla al instanciar."""

        class Incompleta(AbstractMenuRepository):
            pass

        with pytest.raises(TypeError):
            Incompleta()  # type: ignore[abstract]

    def test_subclase_completa_se_puede_instanciar(self):
        """Una subclase que implementa todos los métodos es válida."""

        class Completa(AbstractMenuRepository):
            async def get_all(self) -> list[MenuItem]:
                return []

            async def get_by_id(self, menu_item_id: int) -> MenuItem:
                raise NotImplementedError

            async def add(self, item: MenuItem) -> MenuItem:
                return item

            async def delete(self, menu_item_id: int) -> None:
                pass

        inst = Completa()
        assert isinstance(inst, AbstractMenuRepository)
