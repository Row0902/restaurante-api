"""Tests unitarios de validadores de dominio (core puro, sin mocks)."""

import unittest

from core.exceptions import PlatoInvalido
from core.schemas.plato_create import PlatoCreate
from core.validators.bebida_validator import BebidaValidator
from core.validators.postre_validator import PostreValidator


class TestBebidaValidator(unittest.TestCase):
    """Validación de bebidas — precio máximo 10000."""

    def setUp(self) -> None:
        self.validator = BebidaValidator()

    def test_precio_excede_maximo(self) -> None:
        datos = PlatoCreate(nombre="Vino", precio=15000, categoria="bebida")
        with self.assertRaises(PlatoInvalido):
            self.validator.validar(datos)

    def test_precio_dentro_del_limite(self) -> None:
        datos = PlatoCreate(nombre="Agua", precio=500, categoria="bebida")
        self.validator.validar(datos)


class TestPostreValidator(unittest.TestCase):
    """Validación de postres — descripción obligatoria."""

    def setUp(self) -> None:
        self.validator = PostreValidator()

    def test_sin_descripcion(self) -> None:
        datos = PlatoCreate(nombre="Flan", precio=300, categoria="postre")
        with self.assertRaises(PlatoInvalido):
            self.validator.validar(datos)

    def test_con_descripcion(self) -> None:
        datos = PlatoCreate(
            nombre="Flan",
            descripcion="Flan casero con dulce de leche",
            precio=300,
            categoria="postre",
        )
        self.validator.validar(datos)
