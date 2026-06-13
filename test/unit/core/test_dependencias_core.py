"""Tests de dependencias permitidas para core."""

import importlib
import inspect


def test_core_no_importa_frameworks():
    """Verifica que core no dependa de frameworks externos."""
    modulos = [
        "core.cantidad",
        "core.dominio_error",
        "core.estado_orden",
        "core.item_orden",
        "core.orden",
        "core.plato",
        "core.precio",
    ]

    for nombre_modulo in modulos:
        fuente = inspect.getsource(importlib.import_module(nombre_modulo))
        assert "fastapi" not in fuente.lower()
        assert "pydantic" not in fuente.lower()
        assert "sqlmodel" not in fuente.lower()
