"""Manejadores globales de excepciones de dominio."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions import NoEncontradoError, RestauranteError


def register_error_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de excepciones de dominio."""

    @app.exception_handler(NoEncontradoError)
    async def no_encontrado_handler(
        _request: Request, exc: NoEncontradoError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(RestauranteError)
    async def restaurante_error_handler(
        _request: Request, exc: RestauranteError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
