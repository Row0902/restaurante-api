"""Validador polimórfico para platos de categoría principal."""

from core.exceptions import PlatoInvalido
from core.schemas.plato_create import PlatoCreate
from core.validators.plato_validator import PlatoValidator


class PrincipalValidator(PlatoValidator):
    """Platos principales tienen un precio mínimo de 500."""

    def validar(self, datos: PlatoCreate) -> None:
        if datos.precio < 500:
            raise PlatoInvalido("Un plato principal debe costar al menos 500")
