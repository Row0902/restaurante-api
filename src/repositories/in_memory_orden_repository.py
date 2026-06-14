"""Repositorio en memoria para ordenes."""

from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from core.registro import Registro
from repositories.in_memory_record import copiar_registro


class InMemoryOrdenRepository:
    """Persiste ordenes en un diccionario compartido."""

    def __init__(self, ordenes: dict[str, Registro] | None = None) -> None:
        """Recibe el almacenamiento in-memory."""
        self._ordenes = ordenes if ordenes is not None else {}

    async def listar(self) -> list[Registro]:
        """Devuelve todas las ordenes."""
        return [copiar_registro(orden) for orden in self._ordenes.values()]

    async def guardar(self, orden_id: str, orden: Registro) -> Registro:
        """Guarda una orden."""
        self._ordenes[orden_id] = copiar_registro(orden)
        return copiar_registro(self._ordenes[orden_id])

    async def obtener(self, orden_id: str) -> Registro:
        """Devuelve una orden por ID."""
        self._asegurar_existencia(orden_id)
        return copiar_registro(self._ordenes[orden_id])

    async def actualizar(self, orden_id: str, orden: Registro) -> Registro:
        """Actualiza una orden."""
        self._asegurar_existencia(orden_id)
        self._ordenes[orden_id] = copiar_registro(orden)
        return copiar_registro(self._ordenes[orden_id])

    def _asegurar_existencia(self, orden_id: str) -> None:
        if orden_id not in self._ordenes:
            raise RecursoNoEncontradoError("orden no encontrada")
