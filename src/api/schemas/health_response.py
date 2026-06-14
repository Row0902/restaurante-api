"""Schema de respuesta para health check."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Representa el estado basico de la API."""

    mensaje: str
