"""Configuración de la aplicación."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuraciones globales cargadas desde variables de entorno."""

    app_name: str = "Restaurante API"
    database_url: str = "sqlite+aiosqlite:///./restaurante.db"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
