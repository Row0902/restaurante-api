"""Configuración de la aplicación vía variables de entorno.

Usa pydantic-settings para cargar desde .env o variables del sistema.
Sin valores hardcodeados — R5.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación.

    Attributes:
        DATABASE_URL: URL de conexión a la base de datos SQLite asíncrona.
        APP_NAME: Nombre descriptivo de la aplicación.
        DEBUG: Modo de depuración (False en producción).
    """

    DATABASE_URL: str = "sqlite+aiosqlite:///./restaurante.db"
    APP_NAME: str = "Restaurante API"
    DEBUG: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}
