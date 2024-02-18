from typing import Any


def merge_ui_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Merge two UI configs together. The override config will take precedence over the base config.
    """
    for key, value in override.items():
        if key not in base:
            base[key] = value
        elif isinstance(value, dict):
            base[key] = merge_ui_configs(base[key], value)
        elif isinstance(value, list):
            base[key] = [merge_ui_configs(base[key], item) for item in value]
        else:
            base[key] = value

    return base
