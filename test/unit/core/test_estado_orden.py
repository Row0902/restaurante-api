"""Tests unitarios para EstadoOrden."""

import pytest

from core.dominio_error import DominioError
from core.estado_orden import EstadoOrden


def test_estado_pendiente_puede_pasarse_a_preparacion_o_cancelada():
    """Verifica transiciones iniciales validas."""
    assert EstadoOrden.PENDIENTE.permite_transicion_a(EstadoOrden.EN_PREPARACION)
    assert EstadoOrden.PENDIENTE.permite_transicion_a(EstadoOrden.CANCELADA)


def test_estado_pendiente_no_puede_pasarse_directo_a_entregada():
    """Verifica que no se salte la preparacion."""
    assert not EstadoOrden.PENDIENTE.permite_transicion_a(EstadoOrden.ENTREGADA)


def test_estado_final_no_permite_transiciones():
    """Verifica que estados finales no cambien."""
    assert not EstadoOrden.ENTREGADA.permite_transicion_a(EstadoOrden.CANCELADA)
    assert not EstadoOrden.CANCELADA.permite_transicion_a(EstadoOrden.EN_PREPARACION)


def test_estado_lanza_error_para_transicion_invalida():
    """Verifica error de dominio en transicion invalida."""
    with pytest.raises(DominioError, match="transicion de estado invalida"):
        EstadoOrden.PENDIENTE.validar_transicion_a(EstadoOrden.ENTREGADA)
