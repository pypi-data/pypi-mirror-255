import json
import logging
import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from .....utils import (
    ExtractionQuery,
    PostgresClient,
    SerializedAsset,
    from_env,
)
from ...assets import EXPORTED_FIELDS, MetabaseAsset
from ...errors import EncryptionSecretKeyRequired, MetabaseLoginError
from ..decryption import decrypt
from ..shared import DETAILS_KEY, get_dbname_from_details
from .credentials import CredentialsDb, CredentialsDbKey, get_value

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

SQL_FILE_PATH = "queries/{name}.sql"

ENCRYPTION_SECRET_KEY = "CASTOR_METABASE_ENCRYPTION_SECRET_KEY"  # noqa: S105
REQUIRE_SSL_KEY = "CASTOR_METABASE_REQUIRE_SSL_KEY"  # noqa: S105


def _optional_arg(args: dict, client_key: str, env_key: str) -> Optional[str]:
    arg_value = args.get(client_key)
    if arg_value is not None:
        return arg_value
    return from_env(env_key, allow_missing=True)


class DbClient(PostgresClient):
    """
    Connect to Metabase Database and fetch main assets.
    """

    @staticmethod
    def name() -> str:
        """return the name of the client"""
        return "Metabase/DB"

    def _engine_options(self, credentials: dict) -> dict:
        sslmode = "require" if self.require_ssl else "prefer"
        return {"connect_args": {"sslmode": sslmode}}

    def __init__(
        self,
        **kwargs,
    ):
        self._credentials = CredentialsDb.from_env(kwargs)
        self.encryption_secret_key = _optional_arg(
            kwargs, "encryption_secret_key", ENCRYPTION_SECRET_KEY
        )
        self.require_ssl = bool(
            _optional_arg(kwargs, "require_ssl", REQUIRE_SSL_KEY)
        )
        try:
            super().__init__(self._credentials.to_dict())
        except OperationalError as err:
            raise MetabaseLoginError(
                credentials_info=self._credentials.to_dict(hide=True),
                error_details=err.args,
            )

    def _load_query(self, name: str) -> ExtractionQuery:
        """load SQL text from file"""
        filename = SQL_FILE_PATH.format(name=name)
        path = os.path.join(CURRENT_DIR, filename)
        with open(path, "r") as f:
            content = f.read()
            statement = content.format(schema=self._credentials.schema)
            return ExtractionQuery(statement=statement, params={})

    def base_url(self) -> str:
        """Fetches the `base_url` of the Metabase instance"""
        query = self._load_query(name="base_url")
        rows = list(self.execute(query))
        return rows[0]["value"]

    def _database_specifics(
        self,
        databases: SerializedAsset,
    ) -> SerializedAsset:
        for db in databases:
            assert DETAILS_KEY in db  # this field is expected in database table

            try:
                details = json.loads(db[DETAILS_KEY])
            except json.decoder.JSONDecodeError as err:
                if not self.encryption_secret_key:
                    raise EncryptionSecretKeyRequired(
                        credentials_info=self._credentials.to_dict(hide=True),
                        error_details=err.args,
                    )
                decrypted = decrypt(db[DETAILS_KEY], self.encryption_secret_key)
                details = json.loads(decrypted)

            db["dbname"] = get_dbname_from_details(details)

        return databases

    def fetch(self, asset: MetabaseAsset) -> SerializedAsset:
        """fetches the given asset"""
        query = self._load_query(asset.value.lower())
        assets = list(self.execute(query))

        if asset == MetabaseAsset.DATABASE:
            assets = self._database_specifics(assets)

        logger.info(f"Fetching {asset.name} ({len(assets)} results)")

        # keep interesting fields
        return [
            {key: e.get(key) for key in EXPORTED_FIELDS[asset]} for e in assets
        ]
