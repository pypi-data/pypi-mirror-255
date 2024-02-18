import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod

JWT_PUBLIC_KEY: str
ENCRYPT_PUBLIC_KEY: str
SYNC_KEY: bytes
IS_AMSDAL_SANDBOX_ENVIRONMENT: Incomplete
AMSDAL_ENV_SUBDOMAIN: Incomplete
BASE_AUTH_URL: Incomplete

class AuthHandlerBase(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def validate_credentials(self) -> None: ...
