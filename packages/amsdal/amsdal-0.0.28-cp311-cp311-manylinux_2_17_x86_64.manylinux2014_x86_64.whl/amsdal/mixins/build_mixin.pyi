from _typeshed import Incomplete
from amsdal.configs.constants import CORE_SCHEMAS_PATH as CORE_SCHEMAS_PATH, TYPE_SCHEMAS_PATH as TYPE_SCHEMAS_PATH
from amsdal.configs.main import settings as settings
from amsdal_models.schemas.loaders.cli_fixtures_loader import CliFixturesLoader
from pathlib import Path

class CliMultiFixturesLoader(CliFixturesLoader):
    models_with_fixtures: Incomplete
    def __init__(self, schema_dirs: list[Path]) -> None: ...

class BuildMixin:
    @classmethod
    def build_models(cls, user_schemas_path: Path) -> None: ...
    @staticmethod
    def build_transactions(cli_app_path: Path) -> None: ...
    @staticmethod
    def build_static_files(cli_app_path: Path) -> None: ...
    @staticmethod
    def build_fixtures(cli_app_path: Path) -> None: ...
    @staticmethod
    def _reimport_models() -> None:
        """
        Imports all generated models. Important for cases when models are generated already
        """
