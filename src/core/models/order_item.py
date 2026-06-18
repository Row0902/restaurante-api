"""Entidad Item de Orden — línea de detalle (SQLModel).

Representa la tabla ``order_item``. Cada fila es un plato
dentro de una orden con su cantidad y precio unitario.
"""

from __future__ import annotations

from sqlmodel import Field, SQLModel


class OrderItem(SQLModel, table=True):
    """Línea de detalle de una orden — un plato con cantidad.

    Attributes:
        id: Identificador único.
        order_id: FK a la orden propietaria (se asigna al persistir).
        menu_item_id: FK al plato del menú.
        cantidad: Número de unidades.
        precio_unitario: Precio del plato al momento de la compra.
    """

    __tablename__ = "order_item"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int | None = Field(default=None, foreign_key="order.id")
    menu_item_id: int = Field(foreign_key="menu_item.id")
    cantidad: int = Field(gt=0)
    precio_unitario: float = Field(gt=0)
