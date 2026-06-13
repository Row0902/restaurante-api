"""Valor de dominio para dinero."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from core.dominio_error import DominioError


@dataclass(frozen=True, init=False)
class Precio:
    """Representa un monto monetario no negativo."""

    monto: Decimal

    def __init__(self, monto: Decimal | int | str) -> None:
        """Normaliza y valida el monto."""
        monto_normalizado = self._normalizar(monto)
        self._validar_no_negativo(monto_normalizado)
        object.__setattr__(self, "monto", monto_normalizado)

    def sumar(self, otro: Precio) -> Precio:
        """Devuelve la suma con otro precio."""
        return Precio(self.monto + otro.monto)

    def multiplicar_por(self, cantidad: int) -> Precio:
        """Devuelve el precio multiplicado por una cantidad."""
        return Precio(self.monto * cantidad)

    def _normalizar(self, monto: Decimal | int | str) -> Decimal:
        try:
            return Decimal(str(monto))
        except (InvalidOperation, ValueError) as exc:
            raise DominioError("precio invalido") from exc

    def _validar_no_negativo(self, monto: Decimal) -> None:
        if monto < Decimal("0"):
            raise DominioError("precio no puede ser negativo")
