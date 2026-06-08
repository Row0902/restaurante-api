"""Validador polimórfico para platos de categoría postre."""

from core.exceptions import PlatoInvalido
from core.schemas.plato_create import PlatoCreate
from core.validators.plato_validator import PlatoValidator


class PostreValidator(PlatoValidator):
    """Postres requieren descripción obligatoria."""

    def validar(self, datos: PlatoCreate) -> None:
        if not datos.descripcion:
            raise PlatoInvalido("Un postre debe tener una descripción")
