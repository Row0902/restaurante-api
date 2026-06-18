"""Manejadores de errores globales."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions import DomainException, NotFoundException


def setup_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores de excepciones en la aplicación."""
    
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message},
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message},
        )
