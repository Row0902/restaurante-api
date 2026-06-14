"""Repositorio SQLModel async para ordenes."""

from typing import Any, cast

from sqlalchemy import delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from core.registro import Registro
from repositories.models.orden_item_model import OrdenItemModel
from repositories.models.orden_model import OrdenModel

Numero = str | int | float


class SqlModelOrdenRepository:
    """Persiste ordenes con SQLModel async."""

    def __init__(self, session: AsyncSession) -> None:
        """Recibe la sesion async de trabajo."""
        self._session = session

    async def listar(self) -> list[Registro]:
        """Devuelve todas las ordenes."""
        resultado = await self._session.exec(self._consulta_ordenes())
        return [await self._a_registro(orden) for orden in resultado.all()]

    async def guardar(self, orden_id: str, orden: Registro) -> Registro:
        """Guarda una orden."""
        self._session.add(self._a_modelo(orden_id, orden))
        self._session.add_all(self._items_desde_registro(orden_id, orden))
        await self._session.commit()
        return await self.obtener(orden_id)

    async def obtener(self, orden_id: str) -> Registro:
        """Devuelve una orden por ID."""
        return await self._a_registro(await self._buscar(orden_id))

    async def actualizar(self, orden_id: str, orden: Registro) -> Registro:
        """Actualiza una orden."""
        modelo = await self._buscar(orden_id)
        modelo.total = self._a_float(orden["total"])
        modelo.estado = str(orden["estado"])
        await self._reemplazar_items(orden_id, orden)
        await self._session.commit()
        return await self.obtener(orden_id)

    async def _buscar(self, orden_id: str) -> OrdenModel:
        resultado = await self._session.exec(
            self._consulta_ordenes().where(OrdenModel.id == orden_id),
        )
        modelo = resultado.first()
        if modelo is None:
            raise RecursoNoEncontradoError("orden no encontrada")
        return modelo

    def _consulta_ordenes(self):
        return select(OrdenModel).order_by(OrdenModel.id)

    def _a_modelo(self, orden_id: str, orden: Registro) -> OrdenModel:
        return OrdenModel(
            id=orden_id,
            total=self._a_float(orden["total"]),
            estado=str(orden["estado"]),
        )

    def _items_desde_registro(
        self,
        orden_id: str,
        orden: Registro,
    ) -> list[OrdenItemModel]:
        items = cast(list[Registro], orden.get("items", []))
        return [
            self._item_desde_registro(orden_id, posicion, item)
            for posicion, item in enumerate(items)
        ]

    def _item_desde_registro(
        self,
        orden_id: str,
        posicion: int,
        item: Registro,
    ) -> OrdenItemModel:
        return OrdenItemModel(
            orden_id=orden_id,
            posicion=posicion,
            plato_id=str(item["plato_id"]),
            cantidad=self._a_int(item.get("cantidad", 1)),
        )

    async def _a_registro(self, orden: OrdenModel) -> Registro:
        return {
            "id": orden.id,
            "items": [
                self._item_a_registro(item)
                for item in await self._items_de_orden(orden.id)
            ],
            "total": self._serializar_total(orden.total),
            "estado": orden.estado,
        }

    async def _items_de_orden(self, orden_id: str) -> list[OrdenItemModel]:
        orden_id_columna = cast(Any, OrdenItemModel.orden_id)
        posicion_columna = cast(Any, OrdenItemModel.posicion)
        resultado = await self._session.exec(
            select(OrdenItemModel)
            .where(orden_id_columna == orden_id)
            .order_by(posicion_columna),
        )
        return list(resultado.all())

    async def _reemplazar_items(self, orden_id: str, orden: Registro) -> None:
        orden_id_columna = cast(Any, OrdenItemModel.orden_id)
        await self._session.exec(
            delete(OrdenItemModel).where(orden_id_columna == orden_id),
        )
        self._session.add_all(self._items_desde_registro(orden_id, orden))

    def _item_a_registro(self, item: OrdenItemModel) -> Registro:
        return {"plato_id": item.plato_id, "cantidad": item.cantidad}

    def _serializar_total(self, total: float) -> int | float:
        if total.is_integer():
            return int(total)
        return total

    def _a_float(self, valor: object) -> float:
        return float(cast(Numero, valor))

    def _a_int(self, valor: object) -> int:
        return int(cast(Numero, valor))
