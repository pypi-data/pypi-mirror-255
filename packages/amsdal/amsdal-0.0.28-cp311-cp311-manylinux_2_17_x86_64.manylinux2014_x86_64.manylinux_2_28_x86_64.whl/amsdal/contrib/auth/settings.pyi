from _typeshed import Incomplete
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config: Incomplete
    ADMIN_USER_EMAIL: str | None
    ADMIN_USER_PASSWORD: str | None
    AUTH_JWT_KEY: str | None

auth_settings: Incomplete
