from typing import Any, Dict, List, Optional

from seaplane_framework.api.apis.tags import key_value_api
from seaplane_framework.api.exceptions import ApiException
from seaplane_framework.api.model.key_value_config import KeyValueConfig
from seaplane_framework.api.model.key_value_etag import KeyValueEtag

from seaplane.errors import HTTPError, SeaplaneError
from seaplane.sdk_internal_utils.token_auth import get_pdk_client, method_with_token

SP_STORES = ["_SEAPLANE_INTERNAL"]


class KeyValueStorageAPI:
    """
    Class for handling Key-Value Store API calls.
    """

    _allow_internal: bool
    """
    If set, allows the wrapper to manipulate Seaplane-internal buckets.

    Should not be set in customer code!
    """

    def __init__(self) -> None:
        self._allow_internal = False

    def get_kv_api(self, access_token: str) -> key_value_api.KeyValueApi:
        return key_value_api.KeyValueApi(get_pdk_client(access_token))

    @method_with_token
    def list_stores(self, token: str) -> List[str]:
        """
        List stores

        Returns a List of KV store names
        """
        api = self.get_kv_api(token)
        list = []
        resp = api.list_stores()
        for name in sorted(resp.body):
            if self._allow_internal or name not in SP_STORES:
                list.append(name)

        return list

    @method_with_token
    def create_store(self, token: str, name: str, body: Optional[KeyValueConfig] = None) -> None:
        """
        Create a KV store

        The optional body can be used to configure the store. Example:
        {
            "max_value_size": 8388608,
            "history": 2,
            "ttl": 500,
            "replicas": 3,
            "allow_locations": [
                "region/xn"
            ],
            "deny_locations": [
                "country/nl"
            ]
        }
        """
        if not self._allow_internal and name in SP_STORES:
            raise SeaplaneError(f"Cannot create KV store with Seaplane-internal name `{name}`")

        if not body:
            body = {}

        api = self.get_kv_api(token)
        path_params = {
            "kv_store": name,
        }
        api.create_store(
            path_params=path_params,
            body=body,
        )

    @method_with_token
    def delete_store(self, token: str, name: str) -> None:
        """
        Delete a KV store
        """
        if not self._allow_internal and name in SP_STORES:
            raise SeaplaneError(f"Cannot delete KV store with Seaplane-internal name `{name}`")
        api = self.get_kv_api(token)
        path_params = {
            "kv_store": name,
        }
        api.delete_store(path_params=path_params)

    def exists(self, store: str, key: str) -> bool:
        """
        Check if a key exists in a KV store
        """
        try:
            self.get_key(store, key)
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            raise e
        except HTTPError as e:
            if e.status == 404:
                return False
            raise e

    def get(self, store: str, key: str, default: Any = None) -> Any:
        """
        Get a key value or return the default if key does not exist
        """
        try:
            value = self.get_key(store, key)
            return value
        except ApiException as e:
            if e.status == 404:
                return default
            raise e

    @method_with_token
    def list_keys(self, token: str, store_name: str) -> List[str]:
        """
        List keys in a store

        Returns a List of names of keys in the specified store
        """
        if not self._allow_internal and store_name in SP_STORES:
            raise SeaplaneError(
                f"Cannot list keys in store with Seaplane-internal name `{store_name}`"
            )
        api = self.get_kv_api(token)

        path_params = {
            "kv_store": store_name,
        }
        resp = api.list_keys(
            path_params=path_params,
        )
        list = []
        for name in sorted(resp.body):
            list.append(name)
        return list

    @method_with_token
    def get_key(
        self, token: str, store_name: str, key: str, version_id: Optional[str] = None
    ) -> Any:
        """
        Get a key value

        Optional version_id to get a specific revision
        """
        api = self.get_kv_api(token)
        path_params = {
            "kv_store": store_name,
            "key": key,
        }
        header_params = {} if version_id is None else {"If-Match": KeyValueEtag(version_id)}
        resp = api.get_key(
            path_params=path_params,
            header_params=header_params,
            stream=True,
            accept_content_types=("application/octet-stream",),
            timeout=300,
            skip_deserialization=True,
        )
        return resp.response.read()

    @method_with_token
    def set_key(self, token: str, store_name: str, key: str, value: bytes) -> None:
        """
        Set a key value

        The expected value must be bytes, so if using a string you must encode()
        """
        # TODO: version_id???
        api = self.get_kv_api(token)
        path_params = {
            "kv_store": store_name,
            "key": key,
        }
        header_params: Dict[str, Any] = {}
        api.put_key(
            path_params=path_params,
            header_params=header_params,
            # body=value.encode("utf-8"),  # type: ignore
            body=value,
        )

    @method_with_token
    def delete_key(
        self, token: str, store_name: str, key: str, purge: Optional[bool] = False
    ) -> None:
        """
        Delete a key

        Optional purge bool determines whether older revisions are also purged
        """
        # TODO: version_id???
        api = self.get_kv_api(token)
        path_params = {
            "kv_store": store_name,
            "key": key,
        }
        header_params: Dict[str, Any] = {}
        api.delete_key(
            path_params=path_params,
            header_params=header_params,
            query_params={"purge": "true" if purge else "false"},
        )


kv_store = KeyValueStorageAPI()
