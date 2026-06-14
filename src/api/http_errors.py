"""Traduccion de errores de dominio a errores HTTP."""

from collections.abc import Awaitable

from fastapi import HTTPException

from core.dominio_error import DominioError
from core.recurso_no_encontrado_error import RecursoNoEncontradoError


async def ejecutar_caso_de_uso[T](operacion: Awaitable[T]) -> T:
    """Ejecuta un caso de uso y traduce errores de dominio."""
    try:
        return await operacion
    except RecursoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DominioError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
