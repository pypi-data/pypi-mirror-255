import json
import tempfile
from abc import ABC, abstractmethod
from typing import List

import pandas as pd
from google.cloud import storage

from . import helpers, managers


class AbstractStorageAdapter(ABC):
    @abstractmethod
    def list(self, path: str = "/") -> List[str]:
        pass

    @abstractmethod
    def get(self, path: str) -> str:
        pass

    @abstractmethod
    def put(self, path: str, content: str) -> str:
        pass

    @abstractmethod
    def put_dataframe(self, path: str, df: pd.DataFrame) -> str:
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        pass


class GoogleCloudStorageAdapter(AbstractStorageAdapter):
    NAME = "google_cloud_storage"

    def __init__(self, project: str, name: str, **kwargs) -> None:
        self.project = project
        self.name = name
        self.location = kwargs.get("location", "EU")
        self.storage_class = kwargs.get("storage_class", "STANDARD")
        self.debug = kwargs.get("debug", False)

        self._client = storage.Client(project=project)
        self._bucket = self._get_or_create_bucket(name)
        super().__init__()

    def __repr__(self) -> str:
        return f"GoogleCloudStorageAdapter {json.dumps(self.__dict__, indent=2, default=str)})"

    def __str__(self) -> str:
        return f"gs://{self.name}"

    def _get_or_create_bucket(self, name: str):
        try:
            return self._client.get_bucket(name)
        except Exception:
            bucket = storage.Bucket(self._client, name)
            bucket.location = self.location
            bucket.storage_class = self.storage_class
            self._client.create_bucket(bucket, project=self.project)
            if self.debug:
                print(
                    helpers.bcolors.OKGREEN
                    + f"- Created bucket {name}"
                    + helpers.bcolors.ENDC
                )
            return bucket

    def list(self, path: str = "/") -> List[str]:
        if path == "/":
            path = ""
        datas = self._bucket.list_blobs(prefix=path)
        return [data.name for data in list(datas)]

    def get(self, path: str) -> str:
        return self._bucket.blob(path).download_as_string().decode("utf-8")

    def put(self, path: str, content: str) -> str:
        self._bucket.blob(path).upload_from_string(content)
        return f"gs://{self.name}/{path}"

    def put_dataframe(self, path: str, df: pd.DataFrame) -> str:
        path = f"{path}.parquet"
        with tempfile.NamedTemporaryFile(delete=True) as temp:
            temp_file = f"{temp.name}.parquet"
            df.to_parquet(temp_file, compression="gzip", index=False)
            blob = self._bucket.blob(path)
            blob.upload_from_filename(temp_file)
        return f"gs://{self.name}/{path}"

    def delete(self, path: str) -> None:
        self._bucket.blob(path).delete()


class StorageAdapterManager(managers.AbstractAdapterManager):
    def get(self, name: str, **kwargs) -> AbstractStorageAdapter:
        config = self.config
        cache_key = f"{config.get('project')}-datalake-{kwargs.get('bucket_type')}"
        a = self.datas.get(cache_key)
        if a is not None:
            return a

        if name == GoogleCloudStorageAdapter.NAME:
            a = GoogleCloudStorageAdapter(
                project=config.get("project"),
                location=config.get("location"),
                name=f"{config.get('project')}-datalake-{kwargs.get('bucket_type')}",
                debug=self.debug,
            )
            self.datas[cache_key] = a
            return a
        else:
            raise NotImplementedError(f"StorageAdapter {name} not found")
