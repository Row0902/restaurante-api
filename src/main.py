"""API de restaurante — menú y órdenes."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.menu import router as menu_router
from api.ordenes import router as ordenes_router
from core.exceptions import DomainError, NotFoundError

APP_NAME = "Restaurante API"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "API para la gestión de menú y órdenes de un restaurante."

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle domain not-found errors as 404."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Handle domain errors as 400."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(menu_router)
app.include_router(ordenes_router)


@app.get("/")
async def raiz():
    """Endpoint raíz — health check."""
    return {"mensaje": "API corriendo 👋"}
