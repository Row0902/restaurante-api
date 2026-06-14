"""Traduccion de errores de aplicacion a errores HTTP."""

from collections.abc import Awaitable

from fastapi import HTTPException

from services.aplicacion_error import AplicacionError
from services.caso_de_uso import ejecutar_en_servicio
from services.recurso_aplicacion_no_encontrado_error import (
    RecursoAplicacionNoEncontradoError,
)


async def ejecutar_caso_de_uso[T](operacion: Awaitable[T]) -> T:
    """Ejecuta un caso de uso y traduce errores de aplicacion."""
    try:
        return await ejecutar_en_servicio(operacion)
    except RecursoAplicacionNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AplicacionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
