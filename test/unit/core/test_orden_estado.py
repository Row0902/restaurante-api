"""Tests for the estado state machine with polymorphic transition validation.

Following Strict TDD: RED phase — test written before production code.
"""

import pytest

from core.estado_orden import (
    Cancelado,
    Entregado,
    EstadoOrden,
    Pagado,
    Pendiente,
    Preparando,
    validar_transicion,
)
from core.exceptions import InvalidEstadoTransitionError


class TestEstadoOrdenBase:
    """EstadoOrden is an abstract base class."""

    def test_cannot_instantiate_base(self):
        """EstadoOrden cannot be instantiated directly (abstract)."""
        with pytest.raises(TypeError):
            EstadoOrden("pendiente")  # type: ignore


class TestPendiente:
    """Pendiente transitions: preparando, cancelado."""

    def test_puede_transicionar_a_preparando(self):
        """Pendiente can transition to preparando."""
        estado = Pendiente()
        assert estado.puede_transicionar_a("preparando") is True

    def test_puede_transicionar_a_cancelado(self):
        """Pendiente can transition to cancelado."""
        estado = Pendiente()
        assert estado.puede_transicionar_a("cancelado") is True

    def test_no_puede_transicionar_a_entregado(self):
        """Pendiente cannot transition to entregado."""
        estado = Pendiente()
        assert estado.puede_transicionar_a("entregado") is False

    def test_no_puede_transicionar_a_pagado(self):
        """Pendiente cannot transition to pagado."""
        estado = Pendiente()
        assert estado.puede_transicionar_a("pagado") is False

    def test_no_puede_transicionar_a_inexistente(self):
        """Pendiente cannot transition to an unknown estado."""
        estado = Pendiente()
        assert estado.puede_transicionar_a("inexistente") is False


class TestPreparando:
    """Preparando transitions: entregado, cancelado."""

    def test_puede_transicionar_a_entregado(self):
        """Preparando can transition to entregado."""
        estado = Preparando()
        assert estado.puede_transicionar_a("entregado") is True

    def test_puede_transicionar_a_cancelado(self):
        """Preparando can transition to cancelado."""
        estado = Preparando()
        assert estado.puede_transicionar_a("cancelado") is True

    def test_no_puede_transicionar_a_pendiente(self):
        """Preparando cannot transition back to pendiente."""
        estado = Preparando()
        assert estado.puede_transicionar_a("pendiente") is False

    def test_no_puede_transicionar_a_pagado(self):
        """Preparando cannot transition to pagado."""
        estado = Preparando()
        assert estado.puede_transicionar_a("pagado") is False


class TestEntregado:
    """Entregado transitions: pagado only."""

    def test_puede_transicionar_a_pagado(self):
        """Entregado can transition to pagado."""
        estado = Entregado()
        assert estado.puede_transicionar_a("pagado") is True

    def test_no_puede_transicionar_a_pendiente(self):
        """Entregado cannot transition back to pendiente."""
        estado = Entregado()
        assert estado.puede_transicionar_a("pendiente") is False

    def test_no_puede_transicionar_a_preparando(self):
        """Entregado cannot transition back to preparando."""
        estado = Entregado()
        assert estado.puede_transicionar_a("preparando") is False

    def test_no_puede_transicionar_a_cancelado(self):
        """Entregado cannot transition to cancelado."""
        estado = Entregado()
        assert estado.puede_transicionar_a("cancelado") is False


class TestPagado:
    """Pagado is a terminal state — no transitions allowed."""

    def test_no_puede_transicionar_a_cualquier_estado(self):
        """Pagado rejects all transitions."""
        estado = Pagado()
        assert estado.puede_transicionar_a("pendiente") is False
        assert estado.puede_transicionar_a("preparando") is False
        assert estado.puede_transicionar_a("entregado") is False
        assert estado.puede_transicionar_a("cancelado") is False
        assert estado.puede_transicionar_a("pagado") is False


class TestCancelado:
    """Cancelado is a terminal state — no transitions allowed."""

    def test_no_puede_transicionar_a_cualquier_estado(self):
        """Cancelado rejects all transitions."""
        estado = Cancelado()
        assert estado.puede_transicionar_a("pendiente") is False
        assert estado.puede_transicionar_a("preparando") is False
        assert estado.puede_transicionar_a("entregado") is False
        assert estado.puede_transicionar_a("pagado") is False
        assert estado.puede_transicionar_a("cancelado") is False


class TestValidarTransicion:
    """validar_transicion() helper validates and raises on invalid."""

    def test_valid_transition_pendiente_to_preparando(self):
        """Valid transition from pendiente to preparando passes."""
        # Should not raise
        validar_transicion("pendiente", "preparando")

    def test_valid_transition_pendiente_to_cancelado(self):
        """Valid transition from pendiente to cancelado passes."""
        validar_transicion("pendiente", "cancelado")

    def test_valid_transition_preparando_to_entregado(self):
        """Valid transition from preparando to entregado passes."""
        validar_transicion("preparando", "entregado")

    def test_valid_transition_preparando_to_cancelado(self):
        """Valid transition from preparando to cancelado passes."""
        validar_transicion("preparando", "cancelado")

    def test_valid_transition_entregado_to_pagado(self):
        """Valid transition from entregado to pagado passes."""
        validar_transicion("entregado", "pagado")

    def test_invalid_transition_raises_error(self):
        """Invalid transition raises InvalidEstadoTransitionError."""
        with pytest.raises(InvalidEstadoTransitionError) as excinfo:
            validar_transicion("entregado", "preparando")
        assert "entregado" in str(excinfo.value)
        assert "preparando" in str(excinfo.value)

    def test_invalid_transition_from_terminal_state(self):
        """Transition from pagado raises error."""
        with pytest.raises(InvalidEstadoTransitionError) as excinfo:
            validar_transicion("pagado", "pendiente")
        assert "pagado" in str(excinfo.value)
