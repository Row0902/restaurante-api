"""Exception handlers globales — R15.

Traduce excepciones de dominio a HTTPException con código y mensaje
descriptivo. Sin 500 genéricos por errores no controlados.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions.base import AppBaseError
from core.exceptions.invalid_state import InvalidOrderStateError
from core.exceptions.not_found import MenuItemNotFoundError, OrderNotFoundError


async def menu_item_not_found_handler(
    request: Request,
    exc: MenuItemNotFoundError,
) -> JSONResponse:
    """Traduce MenuItemNotFoundError → 404."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


async def order_not_found_handler(
    request: Request,
    exc: OrderNotFoundError,
) -> JSONResponse:
    """Traduce OrderNotFoundError → 404."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


async def invalid_order_state_handler(
    request: Request,
    exc: InvalidOrderStateError,
) -> JSONResponse:
    """Traduce InvalidOrderStateError → 400."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def app_base_error_handler(
    request: Request,
    exc: AppBaseError,
) -> JSONResponse:
    """Traduce cualquier AppBaseError no capturado → 400."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )
