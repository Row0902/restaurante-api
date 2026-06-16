"""MenuItem SQLModel for the menu_items table.

Naming rationale: ORM model name maps to table name (menu_items),
while Pydantic schemas use domain language (Plato*).
"""

from sqlmodel import Field, SQLModel


class MenuItem(SQLModel, table=True):
    """A menu item in the restaurant's menu.

    Maps to the menu_items table via SQLModel ORM.
    Zero knowledge of HTTP, APIs, or persistence infrastructure.
    """

    __tablename__ = "menu_items"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    precio: float
    categoria: str | None = Field(default=None)
    descripcion: str | None = Field(default=None)
