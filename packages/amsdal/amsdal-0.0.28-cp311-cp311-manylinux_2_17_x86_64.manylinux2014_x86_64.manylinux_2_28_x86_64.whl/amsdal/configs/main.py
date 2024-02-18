import importlib
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias

from pydantic import field_validator
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_prefix='AMSDAL_',
        env_file='.env',
        env_file_encoding='utf-8',
    )

    APP_PATH: Path = Path('.')
    """Path to the app directory where the generated models and other files will be placed."""

    CONFIG_PATH: Path | None = None
    """Path to the config.yml file. If not specified, the default APP_PATH/config.yml file will be used."""

    MODELS_MODULE_NAME: str = 'models'
    """The models module name. The generated models will be placed in this module."""
    SCHEMAS_MODULE_NAME: str = 'schemas'
    """The schemas module name. The schemas will be placed in this module."""
    FIXTURES_MODULE_NAME: str = 'fixtures'
    """The fixtures module name. The fixtures will be placed in this module."""
    STATIC_MODULE_NAME: str = 'static'
    """The static module name. The static files will be placed in this module."""
    TRANSACTIONS_MODULE_NAME: str = 'transactions'
    """The transactions module name. The transactions will be placed in this module."""

    ACCESS_KEY_ID: str | None = None
    """The access key that you will get during registering process."""
    SECRET_ACCESS_KEY: str | None = None
    """The secret access key that you will get during registering process."""
    ACCESS_TOKEN: str | None = None
    """The access token that you will get during sign in process."""

    SANDBOX_ENVIRONMENT: bool | None = None
    """If True, the sandbox environment will be used. If False, the cloud environment will be used."""

    CONTRIBS: list[str] = [
        'amsdal.contrib.auth.app.AuthAppConfig',
        'amsdal.contrib.frontend_configs.app.FrontendConfigAppConfig',
    ]
    """List of contrib modules that will be loaded and used. Can be specified via environment variable AMSDAL_CONTRIBS
    as comma separated string."""

    @field_validator('CONTRIBS', mode='after')
    def load_contrib_modules(cls, value: list[str]) -> list[str]:  # noqa: N805
        from amsdal.contrib.app_config import AppConfig

        for contrib_module in value:
            package_name, class_name = contrib_module.rsplit('.', 1)
            _contrib_module = importlib.import_module(package_name)
            app_config_class: type[AppConfig] = getattr(_contrib_module, class_name)
            app_config_class().on_ready()

        return value

    @property
    def models_root_path(self) -> Path:
        return self.APP_PATH / self.MODELS_MODULE_NAME

    @property
    def schemas_root_path(self) -> Path:
        return self.APP_PATH / self.SCHEMAS_MODULE_NAME

    @property
    def fixtures_root_path(self) -> Path:
        return self.APP_PATH / self.FIXTURES_MODULE_NAME

    @property
    def static_root_path(self) -> Path:
        return self.APP_PATH / self.STATIC_MODULE_NAME

    @property
    def transactions_root_path(self) -> Path:
        return self.models_root_path / self.TRANSACTIONS_MODULE_NAME

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'Settings':
        config_path = self.CONFIG_PATH

        if not config_path:
            self.CONFIG_PATH = self.APP_PATH / 'config.yml'

        return self


if TYPE_CHECKING:
    base: TypeAlias = Settings
else:
    base: TypeAlias = object


class SettingsProxy(base):
    def __init__(self) -> None:
        self._settings = Settings()

    def override(self, **kwargs: Any) -> None:
        new_settings = self._settings.model_dump()
        new_settings.update(kwargs)
        self._settings = Settings(**new_settings)

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._settings.model_dump(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._settings, name)

    def __delattr__(self, name: str) -> None:
        try:
            getattr(self._settings, name)
            self._settings.__delattr__(name)
        except AttributeError:
            msg = f'Settings object has no attribute {name}'
            raise AttributeError(msg) from None

    def __setattr__(self, name: str, value: Any) -> None:
        if name == '_settings':
            super().__setattr__(name, value)
            return

        self._settings.__setattr__(name, value)


settings: SettingsProxy = SettingsProxy()
