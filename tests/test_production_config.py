import pytest

from app.core.config import INSECURE_DEFAULT_DATABASE_URL, Settings


def test_production_rejects_development_database_default() -> None:
    with pytest.raises(ValueError, match="explicit DATABASE_URL"):
        Settings(
            app_environment="production",
            database_url=INSECURE_DEFAULT_DATABASE_URL,
        )


def test_production_rejects_default_development_credentials() -> None:
    with pytest.raises(ValueError, match="default development credentials"):
        Settings(
            app_environment="production",
            database_url="postgresql+psycopg://engineros:engineros@prod-db:5432/engineros",
        )


def test_production_accepts_explicit_non_default_database_credentials() -> None:
    settings = Settings(
        app_environment="production",
        database_url="postgresql+psycopg://engineros_app:replace-via-secret@prod-db:5432/engineros",
    )

    assert settings.app_environment == "production"
