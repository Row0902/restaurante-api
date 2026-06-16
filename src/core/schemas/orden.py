"""Pydantic v2 schemas for orden request/response validation.

Each schema variant implements its own validate() method for polymorphic
validation — no if/match on type. Service layer calls .validate() explicitly.
"""

from datetime import datetime

from pydantic import BaseModel

from core.estado_orden import _ESTADOS
from core.exceptions import InvalidOrdenDataError


class OrdenItemData(BaseModel):
    """Input item within an order creation payload.

    Validates that plato_id and cantidad are positive integers.
    """

    plato_id: int
    cantidad: int

    def validate(self) -> None:  # type: ignore
        """Domain validation — raises InvalidOrdenDataError on failure."""
        if self.plato_id <= 0:
            raise InvalidOrdenDataError("plato_id", "must be positive.")
        if self.cantidad <= 0:
            raise InvalidOrdenDataError("cantidad", "must be positive.")


class OrdenCreate(BaseModel):
    """Input schema for POST /ordenes.

    Requires non-empty items list and validates each item.
    """

    items: list[OrdenItemData]
    mesa: int | None = None

    def validate(self) -> None:  # type: ignore
        """Domain validation — raises InvalidOrdenDataError on failure."""
        if not self.items:
            raise InvalidOrdenDataError("items", "are required.")
        for item in self.items:
            item.validate()


class OrdenUpdateEstado(BaseModel):
    """Input schema for PUT /ordenes/{id}/estado.

    Validates that the target estado is a known state.
    """

    estado: str

    def validate(self) -> None:  # type: ignore
        """Domain validation — raises InvalidOrdenDataError on failure."""
        if self.estado not in _ESTADOS:
            raise InvalidOrdenDataError(
                "estado", f"'{self.estado}' is not a valid estado."
            )


class OrdenItemResponse(BaseModel):
    """Output item schema within an order response.

    Built from OrdenItem ORM model via from_attributes.
    """

    model_config = {"from_attributes": True}

    id: int
    plato_id: int
    cantidad: int
    precio_unitario: float
    nombre: str

    def validate(self) -> None:  # type: ignore
        """No-op for interface consistency with input schemas."""


class OrdenResponse(BaseModel):
    """Output schema for all order responses.

    Built from Orden ORM model via from_attributes.
    """

    model_config = {"from_attributes": True}

    id: int
    items: list[OrdenItemResponse]
    total: float
    estado: str
    created_at: datetime | None = None
    mesa: int | None = None

    def validate(self) -> None:  # type: ignore
        """No-op for interface consistency with input schemas."""
