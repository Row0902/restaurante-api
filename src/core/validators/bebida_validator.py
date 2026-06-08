"""Validador polimórfico para platos de categoría bebida."""

from core.exceptions import PlatoInvalido
from core.schemas.plato_create import PlatoCreate
from core.validators.plato_validator import PlatoValidator


class BebidaValidator(PlatoValidator):
    """Bebidas tienen un precio máximo de 10000."""

    def validar(self, datos: PlatoCreate) -> None:
        if datos.precio > 10000:
            raise PlatoInvalido("El precio de una bebida no puede superar 10000")
