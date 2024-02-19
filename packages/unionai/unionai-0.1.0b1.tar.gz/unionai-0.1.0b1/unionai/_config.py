import base64
import sys
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import version
from os import environ
from typing import Optional

from flyteidl.service.identity_pb2 import UserInfoRequest
from flyteidl.service.identity_pb2_grpc import IdentityServiceStub
from flytekit.clients.auth_helper import get_authenticated_channel
from flytekit.configuration import AuthType, Config, PlatformConfig, get_config_file

_GCP_SERVERLESS_ENDPOINT = "serverless-gcp.cloud-staging.union.ai"
_UNIONAI_SERVERLESS_API_KEY = "UNIONAI_SERVERLESS_API_KEY"
_SERVERLESS_IMAGE_REGISTRY: str = "us-central1-docker.pkg.dev/serverless-gcp-dataplane/union/unionai"


@dataclass
class _UnionAIConfig:
    serverless_endpoint: str = environ.get("UNIONAI_SERVERLESS_ENDPOINT", _GCP_SERVERLESS_ENDPOINT)
    org: Optional[str] = None
    config: Optional[str] = None


_UNIONAI_CONFIG = _UnionAIConfig()


@dataclass
class AppClientCredentials:
    endpoint: str
    client_id: str
    client_secret: str


def _encode_app_client_credentials(app_credentials: AppClientCredentials) -> str:
    """Encode app_credentials with base64."""
    data = f"{app_credentials.endpoint}:{app_credentials.client_id}:{app_credentials.client_secret}"
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def _decode_app_client_credentials(encoded_str: str) -> AppClientCredentials:
    """Decode encoded base64 string into app credentials."""
    endpoint, client_id, client_secret = base64.b64decode(encoded_str.encode("utf-8")).decode("utf-8").split(":")
    return AppClientCredentials(endpoint=endpoint, client_id=client_id, client_secret=client_secret)


def _get_config_obj(config: Optional[str]) -> Config:
    """Get Config object."""
    if config is None:
        config = _UNIONAI_CONFIG.config

    cfg_file = get_config_file(config)
    if cfg_file is None:
        serverless_api_value = environ.get(_UNIONAI_SERVERLESS_API_KEY, None)
        config = Config.for_endpoint(endpoint=_UNIONAI_CONFIG.serverless_endpoint)

        if serverless_api_value is None:
            # Serverless clients points to the serverless endpoint by default.
            return config
        try:
            app_credentials = _decode_app_client_credentials(serverless_api_value)
        except Exception as e:
            raise ValueError(f"Unable to read {_UNIONAI_SERVERLESS_API_KEY}") from e

        return config.with_params(
            platform=PlatformConfig(
                endpoint=app_credentials.endpoint,
                client_id=app_credentials.client_id,
                client_credentials_secret=app_credentials.client_secret,
                auth_mode=AuthType.CLIENTSECRET,
            )
        )
    else:
        # Allow for --config to still be passed in for Managed+ users.
        return Config.auto(config)


def _get_organization(endpoint: str) -> str:
    """Get organization based on endpoint."""
    if _UNIONAI_CONFIG.org is not None:
        return _UNIONAI_CONFIG.org
    elif endpoint == _UNIONAI_CONFIG.serverless_endpoint:
        return _get_serverless_user_handle()
    else:
        # Managed+ users, the org is not required for requests and we set it ""
        # to replicate default flytekit behavior.
        return ""


@lru_cache
def _get_serverless_user_handle() -> str:
    """Get user_handle for serverless."""
    with get_authenticated_channel(
        PlatformConfig.for_endpoint(endpoint=_UNIONAI_CONFIG.serverless_endpoint),
    ) as channel:
        client = IdentityServiceStub(channel)
        user_info = client.UserInfo(UserInfoRequest())
        user_handle = user_info.additional_claims.fields["userhandle"]
        return user_handle.string_value


def _get_default_image() -> Optional[str]:
    """Get default image version."""
    cfg_obj = _get_config_obj(None)

    # TODO: This is only temporary to support GCP endpoints. When the unionai images are public,
    # we will always use unionai images
    if cfg_obj.platform.endpoint == _GCP_SERVERLESS_ENDPOINT:
        major, minor = sys.version_info.major, sys.version_info.minor
        unionai_version = version("unionai")
        if "dev" in unionai_version:
            suffix = "latest"
        else:
            suffix = unionai_version

        return f"{_SERVERLESS_IMAGE_REGISTRY}:py{major}.{minor}-{suffix}"

    # Returning None means that flytekit will use it's default images
    return None
