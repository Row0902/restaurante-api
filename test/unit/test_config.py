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


def test_config_lee_env_file(tmp_path: Path, monkeypatch) -> None:
    """Verifica carga desde archivo .env local."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "APP_NAME=Desde Env File",
                "DEBUG=true",
                "DATABASE_URL=sqlite+aiosqlite:///./env-file.db",
            ],
        ),
        encoding="utf-8",
    )

    config = Config()

    assert config.app_name == "Desde Env File"
    assert config.debug is True
    assert config.database_url == "sqlite+aiosqlite:///./env-file.db"


def test_variables_de_entorno_tienen_precedencia_sobre_env_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Verifica precedencia del entorno del proceso sobre .env."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "APP_NAME=Desde Env File",
                "DEBUG=false",
                "DATABASE_URL=sqlite+aiosqlite:///./env-file.db",
            ],
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("APP_NAME", "Desde Proceso")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./proceso.db")

    config = Config()

    assert config.app_name == "Desde Proceso"
    assert config.debug is True
    assert config.database_url == "sqlite+aiosqlite:///./proceso.db"
