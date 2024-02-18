import base64
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from pydantic import BaseModel

from amsdal.authentication.handlers.base import AMSDAL_ENV_SUBDOMAIN
from amsdal.authentication.handlers.base import ENCRYPT_PUBLIC_KEY
from amsdal.authentication.handlers.client_service import AuthClientService
from amsdal.configs.main import settings
from amsdal.errors import AmsdalDeployError


def _input(msg: str) -> str:
    return input(msg).strip()


def _print(msg: str) -> None:
    print(msg)  # noqa: T201


def want_deploy_input() -> str:
    return _input('Do you want to deploy your app? (y/N): ')


def want_redeploy_input() -> str:
    return _input('Deploy already exists. Do you want to redeploy your app? (y/N): ')


DEPLOY_API_TIMEOUT = 60


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
    def _credentials_data(cls) -> bytes:
        key = serialization.load_pem_public_key(ENCRYPT_PUBLIC_KEY.encode())
        return key.encrypt(  # type: ignore[union-attr]
            json.dumps(
                {
                    'amsdal_access_key_id': settings.ACCESS_KEY_ID,
                    'amsdal_secret_access_key': settings.SECRET_ACCESS_KEY,
                }
            ).encode('utf-8'),
            padding=padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )

    @classmethod
    def deploy_prompt(cls, deploy_type: str, lakehouse_type: str) -> bool:
        want_to_signup = want_deploy_input()

        if want_to_signup.lower() != 'y':
            return False

        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir) / 'app'
            shutil.copytree('src', app_dir / 'src')
            shutil.copy('requirements.txt', app_dir / 'requirements.txt')

            shutil.make_archive('app', 'zip', temp_dir)

        with open('app.zip', 'rb') as f:
            _data = base64.b64encode(f.read()).decode('utf-8')

        Path('app.zip').unlink(missing_ok=True)

        encrypted_data = cls._credentials_data()
        deploy_data = {
            'data': base64.b64encode(encrypted_data).decode('utf-8'),
            'zip_archive': _data,
            'deploy_type': deploy_type,
            'lakehouse_type': lakehouse_type,
        }
        response = AuthClientService().post(
            '/api/transactions/CreateAppDeploy/',
            json=deploy_data,
        )

        if response.status_code != 200:  # noqa: PLR2004
            msg = f'Cannot deploy service: {response.text}'
            raise AmsdalDeployError(msg)

        deploy_response = DeployResponseBaseModel(**response.json())

        if deploy_response.status == 'error':
            if not deploy_response.errors or 'deploy_already_exists' not in deploy_response.errors:
                _print('Deploy failed! Please try again later.')
                return False

            if want_redeploy_input() != 'y':
                return False

            return cls._redeploy(deploy_data)

        deploy_info = DeploymentResponse(**(deploy_response.details or {}))

        client_id = deploy_info.client_id

        _print('Deploy is in progress now. After a few minutes, you can check the status of your deploy.')
        _print(f'Your API domain: https://client-{client_id}.{AMSDAL_ENV_SUBDOMAIN}.amsdal.com/')

        return True

    @classmethod
    def _redeploy(cls, deploy_data: dict[str, Any]) -> bool:
        deploy_data['redeploy'] = True

        response = AuthClientService().post(
            '/api/transactions/CreateAppDeploy/',
            json=deploy_data,
        )

        if response.status_code != 200:  # noqa: PLR2004
            msg = f'Cannot redeploy service: {response.text}'
            raise AmsdalDeployError(msg)

        deploy_response = DeployResponseBaseModel(**response.json())
        if deploy_response.status == 'error':
            _print('Cannot redeploy service! Please try again later.')
            return False

        deploy_info = DeploymentResponse(**(deploy_response.details or {}))
        client_id = deploy_info.client_id

        _print('Deploy is in progress now. After a few minutes, you can check the status of your deploy.')
        _print(f'Your API domain: https://client-{client_id}.{AMSDAL_ENV_SUBDOMAIN}.amsdal.com/')

        return True

    @classmethod
    def list_deploys(cls) -> ListDeployResponseModel | None:
        encrypted_data = cls._credentials_data()
        response = AuthClientService().post(
            '/api/transactions/ListDeploys/',
            json={
                'data': base64.b64encode(encrypted_data).decode('utf-8'),
            },
            timeout=DEPLOY_API_TIMEOUT,
        )

        if response.status_code != 200:  # noqa: PLR2004
            msg = f'Cannot list deploys: {response.text}'
            raise AmsdalDeployError(msg)

        deploy_response = DeployResponseBaseModel(**response.json())

        if deploy_response.status == 'error':
            _print('Cannot list deploys! Please try again later.')
            return None

        return ListDeployResponseModel(**(deploy_response.details or {}))

    @classmethod
    def update_deploy(cls, deployment_id: str) -> UpdateDeployResponseModel | None:
        encrypted_data = cls._credentials_data()
        response = AuthClientService().post(
            '/api/transactions/CheckDeployStatus/',
            json={
                'data': base64.b64encode(encrypted_data).decode('utf-8'),
                'deployment_id': deployment_id,
            },
            timeout=DEPLOY_API_TIMEOUT,
        )

        if response.status_code != 200:  # noqa: PLR2004
            msg = f'Cannot update deploy: {response.text}'
            raise AmsdalDeployError(msg)

        deploy_response = DeployResponseBaseModel(**response.json())

        if deploy_response.status == 'error':
            _print('Deploy with this ID not found.')
            return None

        return UpdateDeployResponseModel(**(deploy_response.details or {}))

    @classmethod
    def destroy_deploy(cls, deployment_id: str) -> bool:
        encrypted_data = cls._credentials_data()
        response = AuthClientService().post(
            '/api/transactions/DestroyAppDeploy/',
            json={
                'data': base64.b64encode(encrypted_data).decode('utf-8'),
                'deployment_id': deployment_id,
            },
            timeout=DEPLOY_API_TIMEOUT,
        )

        if response.status_code != 200:  # noqa: PLR2004
            msg = f'Cannot destroy deploy: {response.text}'
            raise AmsdalDeployError(msg)

        deploy_response = DeployResponseBaseModel(**response.json())

        if deploy_response.status == 'error':
            if deploy_response.errors and 'deploy_not_in_deployed_status' in deploy_response.errors:
                _print('Deploy is not in deployed status. Please refresh deploy status or try again later.')
                return False

            if deploy_response.errors and 'deploy_not_found' in deploy_response.errors:
                _print('Deploy with this ID not found.')
                return False

            _print('Cannot destroy deploy! Please try again later.')
            return False

        _print('Destroying process is in progress now. After a few minutes, you can check the status of your deploy.')

        return True
