from amsdal_utils.lifecycle.enum import LifecycleEvent
from amsdal_utils.lifecycle.producer import LifecycleProducer

from amsdal.contrib.app_config import AppConfig


class AuthAppConfig(AppConfig):
    def on_ready(self) -> None:
        from amsdal.contrib.auth.lifecycle.consumer import AuthenticateUserConsumer
        from amsdal.contrib.auth.lifecycle.consumer import CheckAndCreateSuperUserConsumer
        from amsdal.contrib.auth.lifecycle.consumer import CheckPermissionConsumer

        LifecycleProducer.add_listener(LifecycleEvent.ON_SERVER_STARTUP, CheckAndCreateSuperUserConsumer)
        LifecycleProducer.add_listener(LifecycleEvent.ON_AUTHENTICATE, AuthenticateUserConsumer)
        LifecycleProducer.add_listener(LifecycleEvent.ON_PERMISSION_CHECK, CheckPermissionConsumer)
