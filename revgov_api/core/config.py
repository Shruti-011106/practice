from pydantic_settings import BaseSettings, SettingsConfigDict
from core.constants import (
    ALGORITHM as DEFAULT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES as DEFAULT_TOKEN_EXPIRE,
    REFRESH_TOKEN_EXPIRE_MINUTES as DEFAULT_REFRESH_TOKEN_EXPIRE,
)


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str
    ALGORITHM: str = DEFAULT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = DEFAULT_TOKEN_EXPIRE
    REFRESH_TOKEN_EXPIRE_MINUTES: int = DEFAULT_REFRESH_TOKEN_EXPIRE

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
