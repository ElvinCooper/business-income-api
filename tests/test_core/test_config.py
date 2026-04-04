import os
from unittest.mock import patch

os.environ["JWT_SECRET_KEY"] = "test-key"


def test_settings_defaults():
    from app.core.config import Settings

    settings = Settings()
    assert settings.APP_NAME == "Business Income API"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.DEBUG is True
    assert settings.LOG_LEVEL == "INFO"
    assert settings.JWT_ALGORITHM == "HS256"
    assert isinstance(settings.JWT_EXPIRATION_MINUTES, int)


def test_settings_env_override():
    with patch.dict(
        os.environ,
        {"JWT_SECRET_KEY": "test-key", "APP_NAME": "Custom API", "LOG_LEVEL": "DEBUG"},
        clear=False,
    ):
        from importlib import reload
        import app.core.config as config_module

        reload(config_module)
        settings = config_module.Settings()
        assert settings.APP_NAME == "Custom API"
        assert settings.LOG_LEVEL == "DEBUG"


def test_settings_database_defaults():
    from app.core.config import Settings

    settings = Settings()
    assert isinstance(settings.DB_HOST, str)
    assert isinstance(settings.DB_PORT, int)
    assert isinstance(settings.POSTGRES_HOST, str)
    assert isinstance(settings.POSTGRES_PORT, int)
