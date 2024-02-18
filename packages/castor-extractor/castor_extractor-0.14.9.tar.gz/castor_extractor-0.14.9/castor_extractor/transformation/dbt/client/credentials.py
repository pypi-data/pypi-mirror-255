from dataclasses import dataclass
from enum import Enum
from typing import Dict

from ....utils import from_env


class CredentialsKey(Enum):
    """keys present in dbt credentials"""

    TOKEN = "token"  # noqa: S105
    JOB_ID = "job_id"


CREDENTIALS_ENV: Dict[CredentialsKey, str] = {
    CredentialsKey.TOKEN: "CASTOR_DBT_TOKEN",
    CredentialsKey.JOB_ID: "CASTOR_DBT_JOB_ID",
}


def get_value(key: CredentialsKey, kwargs: dict) -> str:
    """
    Returns the value of the given key:
    - from kwargs in priority
    - from ENV if not provided (raises an error if not found in ENV)
    """
    env_key = CREDENTIALS_ENV[key]
    return str(kwargs.get(key.value) or from_env(env_key))


@dataclass
class DbtCredentials:
    token: str
    job_id: str
