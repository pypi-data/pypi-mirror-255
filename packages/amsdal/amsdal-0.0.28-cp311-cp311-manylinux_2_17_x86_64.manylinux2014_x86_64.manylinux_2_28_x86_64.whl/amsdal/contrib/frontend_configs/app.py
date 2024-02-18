from amsdal_utils.lifecycle.producer import LifecycleProducer

from amsdal.contrib.app_config import AppConfig
from amsdal.contrib.frontend_configs.constants import ON_RESPONSE_EVENT
from amsdal.contrib.frontend_configs.lifecycle.consumer import ProcessResponseConsumer


class FrontendConfigAppConfig(AppConfig):
    def on_ready(self) -> None:
        LifecycleProducer.add_listener(ON_RESPONSE_EVENT, ProcessResponseConsumer)  # type: ignore[arg-type]
