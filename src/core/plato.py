"""Entidad de dominio Plato."""

from dataclasses import dataclass

from core.dominio_error import DominioError
from core.precio import Precio


@dataclass(frozen=True)
class Plato:
    """Representa un plato del menu."""

    id: str
    nombre: str
    precio: Precio

    def __post_init__(self) -> None:
        """Valida identidad y nombre."""
        self._validar_id()
        self._validar_nombre()

    def _validar_id(self) -> None:
        if not self.id.strip():
            raise DominioError("id de plato requerido")

    def _validar_nombre(self) -> None:
        if not self.nombre.strip():
            raise DominioError("nombre de plato requerido")
