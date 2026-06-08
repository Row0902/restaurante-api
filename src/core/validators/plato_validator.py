"""Clase base abstracta para validadores de plato."""

from abc import ABC, abstractmethod

from core.schemas.plato_create import PlatoCreate


class PlatoValidator(ABC):
    """Valida los datos de un PlatoCreate según la categoría."""

    @abstractmethod
    def validar(self, datos: PlatoCreate) -> None:
        """Lanza PlatoInvalido si los datos no cumplen las reglas."""
        ...
