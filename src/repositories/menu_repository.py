"""Contrato de repositorio para menu."""

from typing import Protocol

from core.registro import Registro


class MenuRepository(Protocol):
    """Define operaciones de persistencia para platos."""

    async def listar(self) -> list[Registro]:
        """Devuelve todos los platos."""

    async def guardar(self, plato_id: str, plato: Registro) -> Registro:
        """Guarda un plato."""

    async def obtener(self, plato_id: str) -> Registro:
        """Devuelve un plato por ID."""

    async def actualizar(self, plato_id: str, plato: Registro) -> Registro:
        """Actualiza un plato."""

    async def eliminar(self, plato_id: str) -> Registro:
        """Elimina un plato."""
