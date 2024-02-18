from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_prefix='AMSDAL_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    ADMIN_USER_EMAIL: str | None = None
    ADMIN_USER_PASSWORD: str | None = None
    AUTH_JWT_KEY: str | None = None


auth_settings = Settings()
