"""Entidad Plato del menú (SQLModel).

Representa la tabla ``menu_item`` en la base de datos.
"""

from __future__ import annotations

from sqlmodel import Field, SQLModel


class MenuItem(SQLModel, table=True):
    """Plato del menú del restaurante.

    Attributes:
        id: Identificador único auto-generado por la base de datos.
        nombre: Nombre del plato.
        precio: Precio unitario en decimal.
        descripcion: Descripción opcional.
        categoria: Categoría del plato (Principal, Postre, Bebida, etc.).
    """

    __tablename__ = "menu_item"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=1)
    precio: float = Field(gt=0)
    descripcion: str | None = Field(default=None)
    categoria: str | None = Field(default=None, index=True)
