from amsdal.authentication.handlers.base import AMSDAL_ENV_SUBDOMAIN as AMSDAL_ENV_SUBDOMAIN, ENCRYPT_PUBLIC_KEY as ENCRYPT_PUBLIC_KEY
from amsdal.authentication.handlers.client_service import AuthClientService as AuthClientService
from amsdal.configs.main import settings as settings
from amsdal.errors import AmsdalDeployError as AmsdalDeployError
from pydantic import BaseModel
from typing import Any

def _input(msg: str) -> str: ...
def _print(msg: str) -> None: ...
def want_deploy_input() -> str: ...
def want_redeploy_input() -> str: ...

DEPLOY_API_TIMEOUT: int

class DeployModel(BaseModel):
    deployment_id: str
    status: str

class DeployResponseBaseModel(BaseModel):
    status: str
    details: dict[str, Any] | None
    errors: list[str] | None

class DeploymentResponse(BaseModel):
    status: str
    client_id: str
    deployment_id: str
    created_at: float
    last_update_at: float

class UpdateDeployResponseModel(BaseModel):
    status: str
    deployment_id: str
    created_at: float
    last_update_at: float
    updated: bool

class ListDeployResponseModel(BaseModel):
    deployments: list[DeploymentResponse]

class DeployService:
    @classmethod
    def _credentials_data(cls) -> bytes: ...
    @classmethod
    def deploy_prompt(cls, deploy_type: str, lakehouse_type: str) -> bool: ...
    @classmethod
    def _redeploy(cls, deploy_data: dict[str, Any]) -> bool: ...
    @classmethod
    def list_deploys(cls) -> ListDeployResponseModel | None: ...
    @classmethod
    def update_deploy(cls, deployment_id: str) -> UpdateDeployResponseModel | None: ...
    @classmethod
    def destroy_deploy(cls, deployment_id: str) -> bool: ...
