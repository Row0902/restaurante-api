"""Servicio de aplicacion para menu."""

from repositories.menu_repository import MenuRepository, Registro


class MenuService:
    """Coordina casos de uso de platos del menu."""

    def __init__(self, repo: MenuRepository) -> None:
        """Recibe el repositorio de platos."""
        self._repo = repo

    async def listar(self) -> list[Registro]:
        """Devuelve todos los platos."""
        return await self._repo.listar()

    async def crear(self, plato: Registro) -> Registro:
        """Crea un plato con ID consecutivo segun el estado actual."""
        plato_id = str(len(await self._repo.listar()) + 1)
        nuevo_plato = {"id": plato_id, **plato}
        return await self._repo.guardar(plato_id, nuevo_plato)

    async def obtener(self, plato_id: str) -> Registro:
        """Devuelve un plato por ID."""
        return await self._repo.obtener(plato_id)

    async def actualizar(self, plato_id: str, plato: Registro) -> Registro:
        """Reemplaza los datos de un plato."""
        plato_actualizado = {"id": plato_id, **plato}
        return await self._repo.actualizar(plato_id, plato_actualizado)

    async def eliminar(self, plato_id: str) -> Registro:
        """Elimina un plato y devuelve el mensaje publico actual."""
        await self._repo.eliminar(plato_id)
        return {"mensaje": "Plato eliminado", "id": plato_id}
