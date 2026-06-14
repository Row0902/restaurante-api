"""Error de dominio para recursos inexistentes."""

from core.dominio_error import DominioError


class RecursoNoEncontradoError(DominioError):
    """Indica que un recurso solicitado no existe."""
