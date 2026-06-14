"""Tests unitarios para configuracion de aplicacion."""

from pathlib import Path

from config import Config


def test_config_lee_variables_de_entorno(monkeypatch) -> None:
    """Verifica carga desde entorno real del proceso."""
    monkeypatch.setenv("APP_NAME", "Restaurante Local")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./local.db")

    config = Config()

    assert config.app_name == "Restaurante Local"
    assert config.debug is True
    assert config.database_url == "sqlite+aiosqlite:///./local.db"


def test_config_no_lee_env_file(tmp_path: Path, monkeypatch) -> None:
    """Verifica que no haya dependencia del archivo .env."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("APP_NAME=Desde Env File\n", encoding="utf-8")

    config = Config()

    assert config.app_name == "Restaurante API"
