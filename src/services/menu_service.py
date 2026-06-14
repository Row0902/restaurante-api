"""Servicio de aplicacion para menu."""

from core.plato import Plato
from core.precio import Precio
from core.registro import Registro
from repositories.menu_repository import MenuRepository


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
        nuevo_plato = self._construir_registro(plato_id, plato)
        return await self._repo.guardar(plato_id, nuevo_plato)

    async def obtener(self, plato_id: str) -> Registro:
        """Devuelve un plato por ID."""
        return await self._repo.obtener(plato_id)

    async def actualizar(self, plato_id: str, plato: Registro) -> Registro:
        """Reemplaza los datos de un plato."""
        actual = await self._repo.obtener(plato_id)
        plato_actualizado = self._construir_registro(plato_id, {**actual, **plato})
        return await self._repo.actualizar(plato_id, plato_actualizado)

    async def eliminar(self, plato_id: str) -> Registro:
        """Elimina un plato y devuelve el mensaje publico actual."""
        await self._repo.eliminar(plato_id)
        return {"mensaje": "Plato eliminado", "id": plato_id}

    def _construir_registro(self, plato_id: str, datos: Registro) -> Registro:
        plato = Plato(
            id=plato_id,
            nombre=str(datos.get("nombre", "")),
            precio=Precio(str(datos.get("precio", ""))),
        )
        return {
            "id": plato.id,
            **datos,
            "nombre": plato.nombre,
            "precio": float(plato.precio.monto),
        }
