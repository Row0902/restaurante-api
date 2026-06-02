# src/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "Restaurante API"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./restaurante.db"


settings = Settings()