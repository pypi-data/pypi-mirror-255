from enum import Enum
from typing import Dict

from .....utils import from_env


class CredentialsDbKey(Enum):
    HOST = "host"
    PORT = "port"
    DATABASE = "database"
    SCHEMA = "schema"
    USER = "user"
    PASSWORD = "password"  # noqa: S105


CREDENTIALS_ENV: Dict[CredentialsDbKey, str] = {
    CredentialsDbKey.HOST: "CASTOR_METABASE_DB_HOST",
    CredentialsDbKey.PORT: "CASTOR_METABASE_DB_PORT",
    CredentialsDbKey.DATABASE: "CASTOR_METABASE_DB_DATABASE",
    CredentialsDbKey.SCHEMA: "CASTOR_METABASE_DB_SCHEMA",
    CredentialsDbKey.USER: "CASTOR_METABASE_DB_USERNAME",
    CredentialsDbKey.PASSWORD: "CASTOR_METABASE_DB_PASSWORD",  # noqa: S105
}


def get_value(key: CredentialsDbKey, kwargs: dict) -> str:
    """
    Returns the value of the given key:
    - from kwargs in priority
    - from ENV if not provided (raises an error if not found in ENV)
    """
    env_key = CREDENTIALS_ENV[key]
    return str(kwargs.get(key.value) or from_env(env_key))


class CredentialsDb:
    """ValueObject for the credentials"""

    def __init__(
        self,
        host: str,
        port: str,
        database: str,
        schema: str,
        user: str,
        password: str,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.schema = schema
        self.user = user
        self.password = password

    @classmethod
    def from_env(cls, env: dict) -> "CredentialsDb":
        """returns a new CredentialsDb with values from ENV"""
        return CredentialsDb(
            host=get_value(CredentialsDbKey.HOST, env),
            port=get_value(CredentialsDbKey.PORT, env),
            database=get_value(CredentialsDbKey.DATABASE, env),
            schema=get_value(CredentialsDbKey.SCHEMA, env),
            user=get_value(CredentialsDbKey.USER, env),
            password=get_value(CredentialsDbKey.PASSWORD, env),
        )

    def to_dict(self, hide: bool = False) -> Dict[str, str]:
        safe = (
            CredentialsDbKey.HOST,
            CredentialsDbKey.PORT,
            CredentialsDbKey.DATABASE,
            CredentialsDbKey.SCHEMA,
            CredentialsDbKey.USER,
        )
        unsafe = (CredentialsDbKey.PASSWORD,)

        def val(k: CredentialsDbKey, v: str) -> str:
            return "*" + v[-4:] if hide and k in unsafe else v

        return {a.value: val(a, getattr(self, a.value)) for a in safe + unsafe}
