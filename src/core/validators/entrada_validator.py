"""Validador polimórfico para platos de categoría entrada."""

from core.exceptions import PlatoInvalido
from core.schemas.plato_create import PlatoCreate
from core.validators.plato_validator import PlatoValidator


class EntradaValidator(PlatoValidator):
    """Entradas tienen un precio máximo de 5000."""

    def validar(self, datos: PlatoCreate) -> None:
        if datos.precio > 5000:
            raise PlatoInvalido("El precio de una entrada no puede superar 5000")
