"""Error de aplicacion para reglas de negocio invalidas."""

from services.aplicacion_error import AplicacionError


class ReglaAplicacionError(AplicacionError):
    """Representa una regla de negocio rechazada por la aplicacion."""
