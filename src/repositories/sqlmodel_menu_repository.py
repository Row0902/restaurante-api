"""Repositorio SQLModel async para menu."""

from copy import deepcopy
from typing import cast

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from core.registro import Registro
from repositories.models.plato_model import PlatoModel

CAMPOS_PLATO = {"id", "nombre", "precio"}
Numero = str | int | float


class SqlModelMenuRepository:
    """Persiste platos con SQLModel async."""

    def __init__(self, session: AsyncSession) -> None:
        """Recibe la sesion async de trabajo."""
        self._session = session

    async def listar(self) -> list[Registro]:
        """Devuelve todos los platos."""
        resultado = await self._session.exec(select(PlatoModel).order_by(PlatoModel.id))
        return [self._a_registro(plato) for plato in resultado.all()]

    async def guardar(self, plato_id: str, plato: Registro) -> Registro:
        """Guarda un plato."""
        self._session.add(self._a_modelo(plato_id, plato))
        await self._session.commit()
        return await self.obtener(plato_id)

    async def obtener(self, plato_id: str) -> Registro:
        """Devuelve un plato por ID."""
        return self._a_registro(await self._buscar(plato_id))

    async def actualizar(self, plato_id: str, plato: Registro) -> Registro:
        """Actualiza un plato."""
        modelo = await self._buscar(plato_id)
        modelo.nombre = str(plato["nombre"])
        modelo.precio = self._a_float(plato["precio"])
        modelo.extras = self._extras(plato)
        await self._session.commit()
        return await self.obtener(plato_id)

    async def eliminar(self, plato_id: str) -> Registro:
        """Elimina un plato."""
        modelo = await self._buscar(plato_id)
        registro = self._a_registro(modelo)
        await self._session.delete(modelo)
        await self._session.commit()
        return registro

    async def _buscar(self, plato_id: str) -> PlatoModel:
        modelo = await self._session.get(PlatoModel, plato_id)
        if modelo is None:
            raise RecursoNoEncontradoError("plato no encontrado")
        return modelo

    def _a_modelo(self, plato_id: str, plato: Registro) -> PlatoModel:
        return PlatoModel(
            id=plato_id,
            nombre=str(plato["nombre"]),
            precio=self._a_float(plato["precio"]),
            extras=self._extras(plato),
        )

    def _a_registro(self, plato: PlatoModel) -> Registro:
        return {
            "id": plato.id,
            "nombre": plato.nombre,
            "precio": plato.precio,
            **deepcopy(plato.extras),
        }

    def _extras(self, plato: Registro) -> Registro:
        return deepcopy(
            {
                clave: valor
                for clave, valor in plato.items()
                if clave not in CAMPOS_PLATO
            },
        )

    def _a_float(self, valor: object) -> float:
        return float(cast(Numero, valor))
