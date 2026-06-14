"""Contrato de repositorio para ordenes."""

from typing import Protocol

from core.registro import Registro


class OrdenRepository(Protocol):
    """Define operaciones de persistencia para ordenes."""

    async def listar(self) -> list[Registro]:
        """Devuelve todas las ordenes."""

    async def guardar(self, orden_id: str, orden: Registro) -> Registro:
        """Guarda una orden."""

    async def obtener(self, orden_id: str) -> Registro:
        """Devuelve una orden por ID."""

    async def actualizar(self, orden_id: str, orden: Registro) -> Registro:
        """Actualiza una orden."""
