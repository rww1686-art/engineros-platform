from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


INSECURE_DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://engineros:engineros@db:5432/engineros"
)
PRODUCTION_ENVIRONMENTS = {"production", "prod"}


class Settings(BaseSettings):
    app_name: str = "Engineros Platform"
    app_environment: str = "development"
    database_url: str = INSECURE_DEFAULT_DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        environment = self.app_environment.strip().lower()
        if environment in PRODUCTION_ENVIRONMENTS:
            if self.database_url == INSECURE_DEFAULT_DATABASE_URL:
                raise ValueError(
                    "Production requires an explicit DATABASE_URL; the development default is forbidden."
                )
            if "engineros:engineros@" in self.database_url:
                raise ValueError(
                    "Production DATABASE_URL must not use the default development credentials."
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
