from _typeshed import Incomplete
from pathlib import Path

BASE_DIR: Incomplete
TYPE_SCHEMAS_PATH: Path
CORE_SCHEMAS_PATH: Path
TESTING_ENVIRONMENT: str
DEVELOPMENT_ENVIRONMENT: str
PRODUCTION_ENVIRONMENT: str

def get_default_environment() -> str: ...
