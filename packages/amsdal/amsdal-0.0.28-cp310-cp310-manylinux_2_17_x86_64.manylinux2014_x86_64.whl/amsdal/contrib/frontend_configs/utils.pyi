from typing import Any

def merge_ui_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Merge two UI configs together. The override config will take precedence over the base config.
    """
