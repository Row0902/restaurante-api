"""Valor de dominio para cantidad."""

from dataclasses import dataclass
from operator import index
from typing import SupportsIndex, cast

from core.dominio_error import DominioError


@dataclass(frozen=True, init=False)
class Cantidad:
    """Representa una cantidad entera positiva."""

    valor: int

    def __init__(self, valor: object) -> None:
        """Normaliza y valida la cantidad."""
        valor_normalizado = self._normalizar(valor)
        self._validar_positiva(valor_normalizado)
        object.__setattr__(self, "valor", valor_normalizado)

    def _normalizar(self, valor: object) -> int:
        try:
            return index(cast(SupportsIndex, valor))
        except TypeError as exc:
            raise DominioError("cantidad debe ser un entero") from exc

    def _validar_positiva(self, valor: int) -> None:
        if valor <= 0:
            raise DominioError("cantidad debe ser mayor que cero")
