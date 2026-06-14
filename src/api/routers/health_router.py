"""Router para health check."""

from fastapi import APIRouter

from api.schemas.health_response import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def raiz() -> HealthResponse:
    """Devuelve el estado basico de la API."""
    return HealthResponse(mensaje="API corriendo \U0001f44b")
