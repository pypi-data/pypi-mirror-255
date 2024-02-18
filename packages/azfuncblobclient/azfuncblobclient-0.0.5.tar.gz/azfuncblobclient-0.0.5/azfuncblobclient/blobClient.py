import json
import os

from azfuncbindingbase import Datum, SdkType
from azure.storage.blob import BlobClient as BlobClientSdk
from typing import Union

class BlobClient(SdkType):
    def __init__(self, *, data: Union[bytes, Datum]) -> None:

        # model_binding_data properties
        self._data = data or {}
        self._version = ""
        self._source = ""
        self._content_type = ""
        self._connection = ""
        self._containerName = ""
        self._blobName = ""
        if data is not {}:
            self._version = data.version
            self._source = data.source
            self._content_type = data.content_type
            content_json = json.loads(data.content)
            self._connection = os.getenv(content_json["Connection"])
            self._containerName = content_json["ContainerName"]
            self._blobName = content_json["BlobName"]

    # no getters b/c not exposing any other properties

    # Returns a BlobClient
    def get_sdk_type(self):
        return BlobClientSdk.from_connection_string(
            conn_str=self._connection,
            container_name=self._containerName,
            blob_name=self._blobName
        )