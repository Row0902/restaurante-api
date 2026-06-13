"""Repositorio en memoria para menu."""

from repositories.in_memory_record import copiar_registro
from repositories.menu_repository import Registro


class InMemoryMenuRepository:
    """Persiste platos en un diccionario compartido."""

    def __init__(self, platos: dict[str, Registro] | None = None) -> None:
        """Recibe el almacenamiento in-memory."""
        self._platos = platos if platos is not None else {}

    async def listar(self) -> list[Registro]:
        """Devuelve todos los platos."""
        return [copiar_registro(plato) for plato in self._platos.values()]

    async def guardar(self, plato_id: str, plato: Registro) -> Registro:
        """Guarda un plato."""
        self._platos[plato_id] = copiar_registro(plato)
        return copiar_registro(self._platos[plato_id])

    async def obtener(self, plato_id: str) -> Registro:
        """Devuelve un plato por ID."""
        return copiar_registro(self._platos[plato_id])

    async def actualizar(self, plato_id: str, plato: Registro) -> Registro:
        """Actualiza un plato."""
        self._platos[plato_id] = copiar_registro(plato)
        return copiar_registro(self._platos[plato_id])

    async def eliminar(self, plato_id: str) -> Registro:
        """Elimina un plato."""
        return copiar_registro(self._platos.pop(plato_id))
