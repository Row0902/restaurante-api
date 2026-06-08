from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from services.menu import MenuService


@pytest.mark.asyncio
async def test_listar_platos():
    repo = AsyncMock()

    repo.get_all.return_value = [
        {"id": 1, "nombre": "Pizza"}
    ]

    service = MenuService(repo)

    resultado = await service.listar()

    assert len(resultado) == 1


@pytest.mark.asyncio
async def test_obtener_plato_existente():
    repo = AsyncMock()

    repo.get_by_id.return_value = {
        "id": 1,
        "nombre": "Pizza",
    }

    service = MenuService(repo)

    plato = await service.obtener(1)

    assert plato["id"] == 1


@pytest.mark.asyncio
async def test_obtener_plato_inexistente():
    repo = AsyncMock()

    repo.get_by_id.return_value = None

    service = MenuService(repo)

    with pytest.raises(HTTPException):
        await service.obtener(99)