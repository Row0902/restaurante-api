"""Repositorio en memoria para ordenes."""

from repositories.orden_repository import Registro


class InMemoryOrdenRepository:
    """Persiste ordenes en un diccionario compartido."""

    def __init__(self, ordenes: dict[str, Registro]) -> None:
        """Recibe el almacenamiento in-memory."""
        self._ordenes = ordenes

    async def listar(self) -> list[Registro]:
        """Devuelve todas las ordenes."""
        return list(self._ordenes.values())

    async def guardar(self, orden_id: str, orden: Registro) -> Registro:
        """Guarda una orden."""
        self._ordenes[orden_id] = orden
        return self._ordenes[orden_id]

    async def obtener(self, orden_id: str) -> Registro:
        """Devuelve una orden por ID."""
        return self._ordenes[orden_id]

    async def actualizar(self, orden_id: str, orden: Registro) -> Registro:
        """Actualiza una orden."""
        self._ordenes[orden_id] = orden
        return self._ordenes[orden_id]
