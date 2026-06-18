"""Excepción base del dominio de restaurante.

Todas las excepciones de negocio heredan de aquí para que
la capa API pueda capturarlas y traducirlas a HTTPException — R15.
"""

from __future__ import annotations


class AppBaseError(Exception):
    """Excepción base del dominio.

    Attributes:
        mensaje: Descripción legible del error.
        codigo: Código máquina para identificar el tipo de error.
    """

    def __init__(self, mensaje: str = "", codigo: str = "ERROR") -> None:
        """Inicializa la excepción con mensaje y código.

        Args:
            mensaje: Descripción legible del error.
            codigo: Código máquina para identificar el tipo de error.
        """
        self.codigo = codigo
        super().__init__(mensaje)
