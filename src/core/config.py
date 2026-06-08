"""Configuración de la aplicación vía variables de entorno."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str = "sqlite+aiosqlite:///./restaurante.db"
    app_name: str = "Restaurante API"
    debug: bool = False
    cors_origins: str = "http://localhost:5173,http://localhost:8000"
