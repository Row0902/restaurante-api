"""Fábrica de validadores polimórficos por categoría de plato."""

from core.validators.bebida_validator import BebidaValidator
from core.validators.entrada_validator import EntradaValidator
from core.validators.plato_validator import PlatoValidator
from core.validators.postre_validator import PostreValidator
from core.validators.principal_validator import PrincipalValidator

_VALIDADORES: dict[str, PlatoValidator] = {
    "bebida": BebidaValidator(),
    "principal": PrincipalValidator(),
    "postre": PostreValidator(),
    "entrada": EntradaValidator(),
}


def get_validator(categoria: str) -> PlatoValidator | None:
    """Retorna el validador para la categoría, o None si no hay específico."""
    return _VALIDADORES.get(categoria)
