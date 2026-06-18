"""Tests para la configuración de la aplicación.

Regla R5: sin valores hardcodeados. R13: type hints.
"""

import os
from unittest.mock import patch

from core.config import Settings


class TestSettingsDefaultValues:
    """Verifica valores por defecto cuando no hay .env."""

    def test_app_name_default(self):
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        assert settings.APP_NAME == "Restaurante API"

    def test_debug_default(self):
        settings = Settings(_env_file=None)
        assert settings.DEBUG is False

    def test_database_url_default(self):
        settings = Settings(_env_file=None)
        assert "sqlite+aiosqlite" in settings.DATABASE_URL
        assert settings.DATABASE_URL.endswith(".db")


class TestSettingsFromEnv:
    """Verifica que las variables de entorno se carguen correctamente."""

    def test_carga_database_url_desde_env(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "sqlite+aiosqlite:///./test.db",
                "APP_NAME": "Test API",
                "DEBUG": "true",
            },
            clear=False,
        ):
            settings = Settings(_env_file=None)  # type: ignore[call-arg]
            assert settings.DATABASE_URL == "sqlite+aiosqlite:///./test.db"
            assert settings.APP_NAME == "Test API"
            assert settings.DEBUG is True
