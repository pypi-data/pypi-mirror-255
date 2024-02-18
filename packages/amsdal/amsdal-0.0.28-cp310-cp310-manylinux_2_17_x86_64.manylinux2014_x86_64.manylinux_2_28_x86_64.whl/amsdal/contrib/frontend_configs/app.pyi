from amsdal.contrib.app_config import AppConfig as AppConfig
from amsdal.contrib.frontend_configs.constants import ON_RESPONSE_EVENT as ON_RESPONSE_EVENT
from amsdal.contrib.frontend_configs.lifecycle.consumer import ProcessResponseConsumer as ProcessResponseConsumer

class FrontendConfigAppConfig(AppConfig):
    def on_ready(self) -> None: ...
