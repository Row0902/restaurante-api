"""Error de aplicacion para recursos inexistentes."""

from services.aplicacion_error import AplicacionError


class RecursoAplicacionNoEncontradoError(AplicacionError):
    """Representa un recurso solicitado que no existe."""
