"""Schemas Pydantic para el menú — contratos de API.

DTOs de entrada (request) y salida (response) para los endpoints de menú.
Separados de los modelos SQLModel — R5, R13.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreatePlatoRequest(BaseModel):
    """DTO para crear un nuevo plato.

    Attributes:
        nombre: Nombre del plato (requerido, no vacío).
        precio: Precio unitario (requerido, mayor a cero).
        descripcion: Descripción opcional.
        categoria: Categoría opcional.
    """

    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    descripcion: str | None = None
    categoria: str | None = None


class PlatoResponse(BaseModel):
    """DTO de respuesta para un plato del menú."""

    model_config = {"from_attributes": True}

    id: int
    nombre: str
    precio: float
    descripcion: str | None = None
    categoria: str | None = None
