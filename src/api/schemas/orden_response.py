"""Schema de salida para ordenes."""

from pydantic import BaseModel


class OrdenResponse(BaseModel):
    """Datos publicos de una orden."""

    id: str
    items: list[dict[str, object]]
    total: object
    estado: object
