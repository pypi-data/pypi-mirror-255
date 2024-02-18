import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TYPE_SCHEMAS_PATH: Path = BASE_DIR / 'schemas' / 'types'
CORE_SCHEMAS_PATH: Path = BASE_DIR / 'schemas' / 'core'

# Environment
TESTING_ENVIRONMENT = 'testing'
DEVELOPMENT_ENVIRONMENT = 'development'
PRODUCTION_ENVIRONMENT = 'production'


def get_default_environment() -> str:
    cmd = sys.argv[0] if sys.argv else ''

    if 'pytest' in cmd:
        return TESTING_ENVIRONMENT

    return DEVELOPMENT_ENVIRONMENT
