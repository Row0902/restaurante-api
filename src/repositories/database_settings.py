"""Configuracion de persistencia."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Lee configuracion de base de datos desde entorno."""

    database_url: str = "sqlite+aiosqlite:///./restaurante.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
