"""Casos de uso para la gestión del menú de platos."""

from core.exceptions import PlatoNoEncontrado
from core.models.plato import Plato
from core.schemas.plato_create import PlatoCreate
from core.schemas.plato_read import PlatoRead
from core.schemas.plato_update import PlatoUpdate
from core.validators.factory import get_validator
from repositories.menu import MenuRepository


class MenuService:
    """Casos de uso para el menú. Inyección del repositorio por constructor."""

    def __init__(self, repo: MenuRepository) -> None:
        self._repo = repo

    async def listar(self) -> list[PlatoRead]:
        platos = await self._repo.get_all()
        return [PlatoRead.model_validate(p) for p in platos]

    async def obtener(self, plato_id: int) -> PlatoRead:
        plato = await self._repo.get_by_id(plato_id)
        if plato is None:
            raise PlatoNoEncontrado(plato_id)
        return PlatoRead.model_validate(plato)

    async def crear(self, datos: PlatoCreate) -> PlatoRead:
        validator = get_validator(datos.categoria)
        if validator is not None:
            validator.validar(datos)
        plato = Plato(**datos.model_dump())
        creado = await self._repo.add(plato)
        return PlatoRead.model_validate(creado)

    async def actualizar(self, plato_id: int, datos: PlatoUpdate) -> PlatoRead:
        plato = await self._repo.update(plato_id, datos.model_dump(exclude_unset=True))
        if plato is None:
            raise PlatoNoEncontrado(plato_id)
        return PlatoRead.model_validate(plato)

    async def eliminar(self, plato_id: int) -> None:
        ok = await self._repo.delete(plato_id)
        if not ok:
            raise PlatoNoEncontrado(plato_id)
