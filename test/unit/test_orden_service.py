from unittest.mock import AsyncMock

import pytest

from core.schemas import OrdenCreate, OrdenItem
from services.ordenes import OrdenService


@pytest.mark.asyncio
async def test_crear_orden_calcula_total():
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()

    plato = type(
        "Plato",
        (),
        {"precio": 1000},
    )()

    menu_repo.get_by_id.return_value = plato

    service = OrdenService(
        orden_repo,
        menu_repo,
    )

    orden = OrdenCreate(
        items=[
            OrdenItem(
                plato_id=1,
                cantidad=2,
            )
        ]
    )

    await service.crear(orden)

    orden_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_cambiar_estado():
    orden_repo = AsyncMock()
    menu_repo = AsyncMock()

    orden = type(
        "Orden",
        (),
        {
            "id": 1,
            "estado": "pendiente",
        },
    )()

    orden_repo.get_by_id.return_value = orden

    service = OrdenService(
        orden_repo,
        menu_repo,
    )

    await service.cambiar_estado(
        1,
        "entregado",
    )

    assert orden.estado == "entregado"