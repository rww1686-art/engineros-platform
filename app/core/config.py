from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Engineros Platform"
    app_environment: str = "development"
    database_url: str = "postgresql+psycopg://engineros:engineros@db:5432/engineros"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
