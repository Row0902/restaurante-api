"""Tests para el enum OrderStatus — validación polimórfica de transiciones.

Regla R1 de AGENTS.md: usar polimorfismo, no condicionales.
"""

from core.enums.order_status import OrderStatus


class TestOrderStatusValues:
    """Verifica que los valores del enum sean correctos."""

    def test_pendiente(self):
        assert OrderStatus.pendiente == "pendiente"

    def test_preparando(self):
        assert OrderStatus.preparando == "preparando"

    def test_entregado(self):
        assert OrderStatus.entregado == "entregado"

    def test_cancelado(self):
        assert OrderStatus.cancelado == "cancelado"


class TestOrderStatusTransiciones:
    """Verifica la máquina de estados — CADA estado conoce sus transiciones (R1)."""

    # ── pendiente ──────────────────────────────────────

    def test_pendiente_puede_ir_a_preparando(self):
        assert (
            OrderStatus.pendiente.puede_transicionar_a(OrderStatus.preparando) is True
        )

    def test_pendiente_puede_ir_a_cancelado(self):
        assert OrderStatus.pendiente.puede_transicionar_a(OrderStatus.cancelado) is True

    def test_pendiente_no_puede_ir_a_entregado(self):
        assert (
            OrderStatus.pendiente.puede_transicionar_a(OrderStatus.entregado) is False
        )

    # ── preparando ─────────────────────────────────────

    def test_preparando_puede_ir_a_entregado(self):
        assert (
            OrderStatus.preparando.puede_transicionar_a(OrderStatus.entregado) is True
        )

    def test_preparando_puede_ir_a_cancelado(self):
        assert (
            OrderStatus.preparando.puede_transicionar_a(OrderStatus.cancelado) is True
        )

    def test_preparando_no_puede_volver_a_pendiente(self):
        assert (
            OrderStatus.preparando.puede_transicionar_a(OrderStatus.pendiente) is False
        )

    # ── entregado ──────────────────────────────────────

    def test_entregado_no_puede_ir_a_ningun_lado(self):
        assert (
            OrderStatus.entregado.puede_transicionar_a(OrderStatus.cancelado) is False
        )
        assert (
            OrderStatus.entregado.puede_transicionar_a(OrderStatus.pendiente) is False
        )
        assert (
            OrderStatus.entregado.puede_transicionar_a(OrderStatus.preparando) is False
        )
        assert (
            OrderStatus.entregado.puede_transicionar_a(OrderStatus.entregado) is False
        )

    # ── cancelado ──────────────────────────────────────

    def test_cancelado_no_puede_ir_a_ningun_lado(self):
        assert (
            OrderStatus.cancelado.puede_transicionar_a(OrderStatus.pendiente) is False
        )
        assert (
            OrderStatus.cancelado.puede_transicionar_a(OrderStatus.preparando) is False
        )
        assert (
            OrderStatus.cancelado.puede_transicionar_a(OrderStatus.entregado) is False
        )
        assert (
            OrderStatus.cancelado.puede_transicionar_a(OrderStatus.cancelado) is False
        )

    # ── transición a sí mismo ──────────────────────────

    def test_pendiente_no_puede_transicionar_a_si_mismo(self):
        assert (
            OrderStatus.pendiente.puede_transicionar_a(OrderStatus.pendiente) is False
        )

    def test_preparando_no_puede_transicionar_a_si_mismo(self):
        assert (
            OrderStatus.preparando.puede_transicionar_a(OrderStatus.preparando) is False
        )
