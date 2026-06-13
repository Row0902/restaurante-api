"""Utilidades compartidas por repositorios en memoria."""

from copy import deepcopy

from repositories.menu_repository import Registro


def copiar_registro(registro: Registro) -> Registro:
    """Devuelve una copia independiente del registro."""
    return deepcopy(registro)
