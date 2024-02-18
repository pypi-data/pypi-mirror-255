from importlib.metadata import version
import os
from typing import Dict, Optional

import seaplane_framework.api
import seaplane_framework.config

from seaplane.errors import SeaplaneError
from seaplane.logs import log
from seaplane.sdk_internal_utils.token_api import TokenAPI

import seaplane.run_load_dotenv  # noqa: F401

_SEAPLANE_IDENTIFY_API_ENDPOINT = "https://flightdeck.cplane.cloud/v1"
_SEAPLANE_GLOBAL_SQL_API_ENDPOINT = "https://sql.cplane.cloud/v1"
_SEAPLANE_SQL_DATABASE_ENDPOINT = "sql.cplane.cloud"
_SEAPLANE_CARRIER_API_ENDPOINT = "https://carrier.cplane.cloud/v1"
_SEAPLANE_SUBSTATION_EMBED_API_ENDPOINT = "https://embed.substation.cplane.cloud/v1/embed"
_SEAPLANE_VECTOR_DB_API_ENDPOINT = "https://vector-new.cplane.cloud"

api_key_names = ["SEAPLANE_API_KEY"]


# TODO get_api_keys and associated codepaths are unused, should be removed.
def get_api_keys() -> Dict[str, str]:
    api_keys = {}

    for api_key_env_name in api_key_names:
        api_key = os.environ.get(api_key_env_name)
        if api_key:
            api_keys[api_key_env_name] = api_key

    return api_keys


def _default_runner_image() -> str:
    sdk_version = version("seaplane")
    return f"us-central1-docker.pkg.dev/artifacts-356722/sdk-apps/apps-executor:{sdk_version}"


class Configuration:
    """
    Seaplane SDK Configuration.

    Everytime the configuration is changed,
    It'll clear local configurations to the default Auth module.
    """

    def __init__(self) -> None:
        self.region: Optional[str] = None
        self.dc_region: Optional[str] = None
        self.identify_endpoint = _SEAPLANE_IDENTIFY_API_ENDPOINT
        self.global_sql_endpoint = _SEAPLANE_GLOBAL_SQL_API_ENDPOINT
        self.sql_database_endpoint = _SEAPLANE_SQL_DATABASE_ENDPOINT
        self.carrier_endpoint = _SEAPLANE_CARRIER_API_ENDPOINT
        self.vector_db_endpoint = _SEAPLANE_VECTOR_DB_API_ENDPOINT
        self.substation_embed_endpoint = _SEAPLANE_SUBSTATION_EMBED_API_ENDPOINT
        self.runner_image = os.environ.get("SEAPLANE_RUNNER_IMAGE", _default_runner_image())
        self.name_prefix = os.environ.get("SEAPLANE_NAME_PREFIX", "")
        self._api_keys: Dict[str, str] = get_api_keys()
        self._production = False

        seaplane_api_key = os.environ.get("SEAPLANE_API_KEY")
        self._token_api = TokenAPI(url=f"{self.identify_endpoint}/token", api_key=seaplane_api_key)

    def set_api_key(self, api_key: str) -> None:
        """Set the Seaplane API Key.

        The API Key is needed for the Seaplane Python SDK usage.

        Parameters
        ----------
        api_key : str
            Seaplane API Key.
        """
        self._token_api.set_api_key(api_key)

    def set_api_keys(self, api_keys: Dict[str, str]) -> None:
        """Set the Seaplane API Keys for Apps.

        The API Keys is needed for some of the Tasks.

        Supported Tasks API Keys:

        Seaplane: SEAPLANE_API_KEY

        For example, for use an OpenAI Task,
        you need to provide the Key - Value, of the API Key.

            $ from seaplane import sea

            $ api_keys = {"OPENAI_API_KEY": "sp-api-key-test" }
            $ sea.config.set_api_keys(api_keys)

        Parameters
        ----------
        api_keys : object
            API Keys and values.
        """

        if api_keys is None:
            raise SeaplaneError("api_keys parameters can't be None")
        self._api_keys = api_keys
        if api_keys.get("SEAPLANE_API_KEY", None) is not None:
            self.set_api_key(api_keys["SEAPLANE_API_KEY"])
            self._api_keys.pop("SEAPLANE_API_KEY")

    def set_identify_endpoint(self, endpoint: str) -> None:
        if endpoint[-1] == "/":
            self.identify_endpoint = endpoint.rstrip(endpoint[-1])
        else:
            self.identify_endpoint = endpoint

        self._token_api.set_url(url=f"{self.identify_endpoint}/token")

    def set_global_sql_endpoint(self, endpoint: str) -> None:
        if endpoint[-1] == "/":
            self.global_sql_endpoint = endpoint.rstrip(endpoint[-1])
        else:
            self.global_sql_endpoint = endpoint

    def set_sql_database_endpoint(self, endpoint: str) -> None:
        if endpoint[-1] == "/":
            self.sql_database_endpoint = endpoint.rstrip(endpoint[-1])
        else:
            self.sql_database_endpoint = endpoint

    def set_carrier_endpoint(self, endpoint: str) -> None:
        if endpoint[-1] == "/":
            self.carrier_endpoint = endpoint.rstrip(endpoint[-1])
        else:
            self.carrier_endpoint = endpoint

    def set_vector_endpoint(self, endpoint: str) -> None:
        if endpoint[-1] == "/":
            self.vector_db_endpoint = endpoint.rstrip(endpoint[-1])
        else:
            self.vector_db_endpoint = endpoint

    def set_substation_embed_endpoint(self, endpoint: str) -> None:
        if endpoint[-1] == "/":
            self.substation_embed_endpoint = endpoint.rstrip(endpoint[-1])
        else:
            self.substation_embed_endpoint = endpoint

    def log_level(self, level: int) -> None:
        """Change logging level.
        Seaplane uses Python logging module for internal logs.
        Python logging levels can be used directly with Seaplane Python SDK or
        use the already defined in seaplane.log module.
            $ from seaplane import sea, log
            $ sea.config.log_level(log.INFO)
        Parameters
        ----------
        level : int
            Logging Level from Python logging module,
            like DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        log.level(level)

        if level == log.DEBUG:
            log.debug("Seaplane debug activated")
            log.debug(f"Identify endpoint: {self.identify_endpoint}")
            log.debug(f"Carrier endpoint: {self.carrier_endpoint}")
            log.debug(f"Vector endpoint: {self.vector_db_endpoint}")

    def log_enable(self, enable: bool) -> None:
        """Enable or disable the Seaplane logging for the SDK.

        Parameters
        ----------
        enable : bool
            True to enable, False to disable.
        """
        if enable:
            log.enable()
        else:
            log.disable()

    def staging_mode(self) -> None:
        self.set_global_sql_endpoint("https://sql.staging.cplane.dev/v1")
        self.set_sql_database_endpoint("sql.staging.cplane.dev")
        self.set_carrier_endpoint("https://carrier.staging.cplane.dev/v1")
        self.set_identify_endpoint("https://flightdeck.staging.cplane.dev/v1")
        self.set_vector_endpoint("https://vector-new.staging.cplane.dev")

    def set_region(self, region: str) -> None:
        self.region = region.lower()
        if self.region in {"xa"}:
            self.dc_region = "sin"
        elif self.region in {"xe", "xf", "xu"}:
            self.dc_region = "fra"
        else:
            self.dc_region = "sjc"

    def get_platform_configuration(self) -> seaplane_framework.api.Configuration:
        configuration = seaplane_framework.api.Configuration()
        configuration.host = self.carrier_endpoint
        return configuration

    def get_access_token(self) -> str | None:
        return self._token_api.access_token


config = Configuration()
