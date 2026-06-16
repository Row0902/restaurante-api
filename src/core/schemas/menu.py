"""Pydantic v2 schemas for menu request/response validation.

Each schema variant implements its own validate() method for polymorphic
validation — no if/match on type. Service layer calls .validate() explicitly.
"""

from pydantic import BaseModel

from core.exceptions import InvalidMenuDataError


class PlatoCreate(BaseModel):
    """Input schema for POST /menu.

    Requires non-empty nombre and positive precio.
    """

    nombre: str
    precio: float
    categoria: str | None = None
    descripcion: str | None = None

    def validate(self) -> None:  # type: ignore
        """Domain validation — raises InvalidMenuDataError on failure."""
        if not self.nombre:
            raise InvalidMenuDataError("nombre", "is required.")
        if self.precio <= 0:
            raise InvalidMenuDataError("precio", "must be positive.")


class PlatoUpdate(BaseModel):
    """Input schema for PUT /menu.

    All fields optional. Only validates fields that are explicitly provided.
    """

    nombre: str | None = None
    precio: float | None = None
    categoria: str | None = None
    descripcion: str | None = None

    def validate(self) -> None:  # type: ignore
        """Domain validation — only checks non-None fields."""
        if self.nombre is not None and not self.nombre:
            raise InvalidMenuDataError("nombre", "is required.")
        if self.precio is not None and self.precio <= 0:
            raise InvalidMenuDataError("precio", "must be positive.")


class PlatoResponse(BaseModel):
    """Output schema for all menu responses.

    Built from MenuItem ORM model via from_attributes.
    """

    model_config = {"from_attributes": True}

    id: int
    nombre: str
    precio: float
    categoria: str | None = None
    descripcion: str | None = None

    def validate(self) -> None:  # type: ignore
        """No-op for interface consistency with PlatoCreate/PlatoUpdate."""
