"""Ejecucion de casos de uso con traduccion de errores de dominio."""

from collections.abc import Awaitable

from core.dominio_error import DominioError
from core.recurso_no_encontrado_error import RecursoNoEncontradoError
from services.recurso_aplicacion_no_encontrado_error import (
    RecursoAplicacionNoEncontradoError,
)
from services.regla_aplicacion_error import ReglaAplicacionError


async def ejecutar_en_servicio[T](operacion: Awaitable[T]) -> T:
    """Ejecuta una operacion y expone solo errores de aplicacion."""
    try:
        return await operacion
    except RecursoNoEncontradoError as exc:
        raise RecursoAplicacionNoEncontradoError(str(exc)) from exc
    except DominioError as exc:
        raise ReglaAplicacionError(str(exc)) from exc
