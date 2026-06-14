"""Configuracion de aplicacion."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Lee configuracion desde variables de entorno."""

    app_name: str = "Restaurante API"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./restaurante.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def cargar_config() -> Config:
    """Carga configuracion de aplicacion."""
    return Config()
