"""Configuración global de la aplicación FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import register_error_handlers
from core.config import Settings


def configure_app(app: FastAPI) -> None:
    """Configura middlewares y manejadores globales de la aplicación."""
    settings = Settings()

    _origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Content-Type", "Authorization"],
    )

    register_error_handlers(app)
