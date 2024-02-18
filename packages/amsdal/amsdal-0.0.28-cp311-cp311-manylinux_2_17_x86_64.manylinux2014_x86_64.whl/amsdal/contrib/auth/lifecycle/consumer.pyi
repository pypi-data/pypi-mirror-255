from _typeshed import Incomplete
from amsdal.contrib.auth.errors import AuthenticationError as AuthenticationError
from amsdal_models.classes.model import Model
from amsdal_utils.lifecycle.consumer import LifecycleConsumer
from typing import Any

logger: Incomplete

class CheckAndCreateSuperUserConsumer(LifecycleConsumer):
    def on_event(self) -> None: ...

class AuthenticateUserConsumer(LifecycleConsumer):
    def on_event(self, auth_header: str, authentication_info: Any) -> None: ...

class CheckPermissionConsumer(LifecycleConsumer):
    def on_event(self, object_class: type[Model], user: Any, access_types: list[Any], permissions_info: Any) -> None: ...
