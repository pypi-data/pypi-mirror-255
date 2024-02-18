from collections.abc import Generator
from importlib import import_module
from pathlib import Path


def get_contrib_schemas_paths() -> Generator[Path, None, None]:
    from amsdal.configs.main import settings

    for contrib in settings.CONTRIB:
        module_name, *_ = contrib.rsplit('.', 2)
        module = import_module(module_name)

        yield Path(module.__file__).parent / 'models'  # type: ignore[arg-type]
