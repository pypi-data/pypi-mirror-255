from _typeshed import Incomplete
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Any, TypeAlias

class Settings(BaseSettings):
    model_config: Incomplete
    APP_PATH: Path
    CONFIG_PATH: Path | None
    MODELS_MODULE_NAME: str
    SCHEMAS_MODULE_NAME: str
    FIXTURES_MODULE_NAME: str
    STATIC_MODULE_NAME: str
    TRANSACTIONS_MODULE_NAME: str
    ACCESS_KEY_ID: str | None
    SECRET_ACCESS_KEY: str | None
    ACCESS_TOKEN: str | None
    SANDBOX_ENVIRONMENT: bool | None
    CONTRIBS: list[str]
    def load_contrib_modules(cls, value: list[str]) -> list[str]: ...
    @property
    def models_root_path(self) -> Path: ...
    @property
    def schemas_root_path(self) -> Path: ...
    @property
    def fixtures_root_path(self) -> Path: ...
    @property
    def static_root_path(self) -> Path: ...
    @property
    def transactions_root_path(self) -> Path: ...
    def check_passwords_match(self) -> Settings: ...

base: TypeAlias

class SettingsProxy(base):
    _settings: Incomplete
    def __init__(self) -> None: ...
    def override(self, **kwargs: Any) -> None: ...
    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...
    def __getattr__(self, name: str) -> Any: ...
    def __delattr__(self, name: str) -> None: ...
    def __setattr__(self, name: str, value: Any) -> None: ...

settings: SettingsProxy
