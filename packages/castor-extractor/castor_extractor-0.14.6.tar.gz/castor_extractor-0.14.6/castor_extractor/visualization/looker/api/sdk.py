"""
This file is a proxy to Looker SDK functions using Castor ApiSettings.
"""

from typing import Optional

from looker_sdk.error import SDKError
from looker_sdk.rtl import (
    auth_session,
    requests_transport,
    serialize,
    transport,
)
from looker_sdk.rtl.api_settings import PApiSettings, SettingsConfig
from looker_sdk.sdk import constants
from looker_sdk.sdk.api40 import methods as methods40
from looker_sdk.sdk.api40.models import (
    Dashboard,
    DashboardElement,
    DBConnection,
    Folder,
    GroupHierarchy,
    GroupSearch,
    Look,
    LookmlModel,
    LookmlModelExplore,
    LookmlModelExploreField,
    LookmlModelExploreFieldset,
    LookmlModelExploreJoins,
    LookmlModelNavExplore,
    Project,
    Query,
    User,
)
from typing_extensions import Protocol

from ..env import timeout_second


class Credentials:
    """ValueObject for the credentials"""

    def __init__(
        self,
        *,
        base_url: str,
        client_id: str,
        client_secret: str,
        timeout: Optional[int] = None,
        **_kwargs,
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout: int = timeout or timeout_second()

    def to_settings_config(self) -> SettingsConfig:
        return SettingsConfig(
            base_url=self.base_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            timeout=str(self.timeout),
        )


def has_admin_permissions(sdk_: methods40.Looker40SDK) -> bool:
    """Check if any of the current user's permissions include admin rights"""
    current_user_id = sdk_.me().id
    if not current_user_id:
        return False
    current_user_roles = sdk_.user_roles(current_user_id)
    return any(
        "administer" in role.permission_set.permissions
        for role in current_user_roles
        if role.permission_set and role.permission_set.permissions
    )


def init40(config: Credentials) -> methods40.Looker40SDK:
    """Default dependency configuration"""
    settings = ApiSettings(config=config, sdk_version=constants.sdk_version)
    settings.is_configured()
    transport = requests_transport.RequestsTransport.configure(settings)
    return methods40.Looker40SDK(
        auth=auth_session.AuthSession(
            settings,
            transport,
            serialize.deserialize40,
            "4.0",
        ),
        deserialize=serialize.deserialize40,
        serialize=serialize.serialize40,
        transport=transport,
        api_version="4.0",
    )


class CastorApiSettings(PApiSettings):
    """This is an intermediate class that is meant to be extended (for typing purpose)"""

    def read_config(self) -> SettingsConfig:
        raise NotImplementedError()


class ApiSettings(CastorApiSettings):
    """SDK settings with initialisation using a credential object instead of a path to a .ini file"""

    def __init__(self, config: Credentials, sdk_version: Optional[str] = ""):
        """Configure using a config dict"""
        self.config = config.to_settings_config()
        self.verify_ssl = True
        self.base_url = self.config.get("base_url", "")
        self.timeout = config.timeout
        self.headers = {"Content-Type": "application/json"}
        self.agent_tag = f"{transport.AGENT_PREFIX}"
        if sdk_version:
            self.agent_tag += f" {sdk_version}"

    def read_config(self) -> SettingsConfig:
        """Returns a serialization of the credentials"""
        return self.config
