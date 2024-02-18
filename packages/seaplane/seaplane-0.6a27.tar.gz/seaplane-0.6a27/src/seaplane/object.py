from typing import cast, Any, Dict, List, Optional, TypedDict

import requests
from seaplane_framework.api.apis.tags import object_api
from seaplane_framework.api.model.bucket import Bucket

from seaplane.config import config
from seaplane.errors import HTTPError, SeaplaneError
from seaplane.sdk_internal_utils.http import headers
from seaplane.sdk_internal_utils.token_auth import get_pdk_client, method_with_token

SP_BUCKETS = ["seaplane-internal-flows"]


class ListObjectsMetadata(TypedDict):
    """
    Dictionary wrapping the metadata returned by the `list_objects()` endpoint.
    """

    name: str
    digest: str
    mod_time: int
    size: int


class ObjectStorageAPI:
    """
    Class for handling Object Storage API calls.
    """

    _allow_internal: bool
    """
    If set, allows the wrapper to manipulate Seaplane-internal buckets.

    Should not be set in customer code!
    """

    def __init__(self) -> None:
        self._allow_internal = False

    def get_object_api(self, access_token: str) -> object_api.ObjectApi:
        return object_api.ObjectApi(get_pdk_client(access_token))

    @method_with_token
    def list_buckets(self, token: str) -> List[str]:
        """
        Returns a list of buckets
        """
        api = self.get_object_api(token)
        list = []
        resp = api.list_buckets()
        for name, _ in sorted(resp.body.items()):
            if self._allow_internal or name not in SP_BUCKETS:
                list.append(name)

        return list

    @method_with_token
    def get_bucket(self, token: str, name: str) -> Dict[str, Any]:
        """
        Get metadata about a bucket
        """
        api = self.get_object_api(token)
        resp = api.get_bucket(path_params={"bucket_name": name})
        return {k: cast(str, v) for (k, v) in resp.body.items()}

    @method_with_token
    def create_bucket(self, token: str, name: str, body: Optional[Bucket] = None) -> None:
        """
        Create a new bucket

        Optional body argument can be used to configure the bucket with description, notify, etc.
        """
        if not self._allow_internal and name in SP_BUCKETS:
            raise SeaplaneError(f"Cannot create bucket with Seaplane-internal name `{name}`")

        if not body:
            body = {}

        api = self.get_object_api(token)
        path_params = {
            "bucket_name": name,
        }
        api.create_bucket(
            path_params=path_params,
            body=body,
        )

    @method_with_token
    def delete_bucket(self, token: str, name: str) -> None:
        """
        Delete a bucket
        """
        if not self._allow_internal and name in SP_BUCKETS:
            raise SeaplaneError(f"Cannot delete bucket with Seaplane-internal name `{name}`")
        api = self.get_object_api(token)
        path_params = {
            "bucket_name": name,
        }
        api.delete_bucket(path_params=path_params)

    def exists(self, bucket: str, object: str) -> bool:
        """
        Returns True if object exists in bucket
        """
        try:
            objs = self.list_objects(bucket, "")
            for obj in objs:
                if obj["name"] == object:
                    return True
            return False
        except HTTPError as e:
            if e.status == 404:
                return False
            raise e

    @method_with_token
    def list_objects(
        self, token: str, bucket_name: str, path_prefix: str = "/"
    ) -> List[ListObjectsMetadata]:
        """
        List objects in a bucket, (optional) matching a path prefix

        Returns a list of dicts with name, digest, mod_time, and bytes for each object
        """
        if not self._allow_internal and bucket_name in SP_BUCKETS:
            raise SeaplaneError(
                f"Cannot list objects in bucket with Seaplane-internal name `{bucket_name}`"
            )
        api = self.get_object_api(token)

        path_params = {
            "bucket_name": bucket_name,
        }
        query_params = {
            "path": path_prefix,
        }
        resp = api.list_objects(
            path_params=path_params,
            query_params=query_params,
        )

        table = [
            ListObjectsMetadata(
                name=x["name"],
                digest=x["digest"],
                mod_time=x["mod_time"],
                size=x["size"],
            )
            for x in resp.body
        ]

        return table

    @method_with_token
    def download(self, token: str, bucket_name: str, path: str) -> bytes:
        """
        Downloads an object

        Returns the object in bytes
        """
        url = f"{config.carrier_endpoint}/object/{bucket_name}/store"

        params: Dict[str, Any] = {}
        params["path"] = path
        resp = requests.get(
            url,
            params=params,
            headers=headers(token, "application/octet-stream"),
        )
        return resp.content

    def file_url(self, bucket_name: str, path: str) -> str:
        """
        Builds a URL usable to download the object stored at the given bucket & path.
        """
        return f"{config.carrier_endpoint}/object/{bucket_name}/store?path={path}"

    @method_with_token
    def upload(self, token: str, bucket_name: str, path: str, object: bytes) -> None:
        """
        Create a new object from the given object data (bytes)
        """
        if not self._allow_internal and bucket_name in SP_BUCKETS:
            raise SeaplaneError(
                f"Cannot upload to bucket with Seaplane-internal name `{bucket_name}`"
            )
        api = self.get_object_api(token)

        path_params = {
            "bucket_name": bucket_name,
        }
        query_params = {
            "path": path,
        }

        api.create_object(
            path_params=path_params,
            query_params=query_params,
            body=object,
        )

    def upload_file(self, bucket_name: str, path: str, object_path: str) -> None:
        """
        Upload a local file to a new object
        """
        if not self._allow_internal and bucket_name in SP_BUCKETS:
            raise SeaplaneError(
                f"Cannot upload to bucket with Seaplane-internal name `{bucket_name}`"
            )
        with open(object_path, "rb") as file:
            file_data = file.read()

        self.upload(bucket_name, path, file_data)

    @method_with_token
    def delete(self, token: str, bucket_name: str, path: str) -> None:
        """
        Delete an object
        """
        if not self._allow_internal and bucket_name in SP_BUCKETS:
            raise SeaplaneError(
                f"Cannot delete from bucket with Seaplane-internal name `{bucket_name}`"
            )
        api = self.get_object_api(token)
        path_params = {
            "bucket_name": bucket_name,
        }
        query_params = {
            "path": path,
        }
        api.delete_object(
            path_params=path_params,
            query_params=query_params,
        )


object_store = ObjectStorageAPI()
