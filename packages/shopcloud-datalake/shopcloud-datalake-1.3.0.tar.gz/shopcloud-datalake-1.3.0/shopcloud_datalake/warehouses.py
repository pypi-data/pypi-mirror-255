from abc import ABC, abstractmethod

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from . import managers


class WarehouseAdapter(ABC):
    @abstractmethod
    def push(self, name: str, file_uri: str) -> None:
        pass


class WarehouseBigQueryAdapter(WarehouseAdapter):
    NAME = "bigquery"

    def __init__(self, project: str, location: str, dataset: str, **kwargs) -> None:
        self.project = project
        self.location = location
        self.dataset = dataset
        self.debug = kwargs.get("debug", False)

    def _push(self, name: str, file_uri: str, job_config) -> None:
        client = bigquery.Client()

        dataset_id = f"{self.project}.{self.dataset}"
        try:
            client.get_dataset(dataset_id)
        except NotFound:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = self.location
            dataset = client.create_dataset(dataset)
            if self.debug:
                print(
                    f"- [{self.__class__.__name__}] Created dataset {dataset.full_dataset_id}"
                )

        table_id = f"{self.project}.{self.dataset}.{name}"
        load_job = client.load_table_from_uri(
            file_uri,
            table_id,
            job_config=job_config,
        )
        load_job.result()
        if self.debug:
            print(
                f"- [{self.__class__.__name__}] Loaded {load_job.output_rows} rows into {table_id}"
            )

    def push(self, name: str, file_uri: str) -> None:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.PARQUET,
        )
        return self._push(
            name=name,
            file_uri=file_uri,
            job_config=job_config,
        )


class WarehouseManager(managers.AbstractAdapterManager):
    def get(self, name: str, **kwargs):
        a = self.datas.get(name)
        if a is not None:
            return a

        if name == WarehouseBigQueryAdapter.NAME:
            config = {
                **{
                    "dataset": "datalake",
                },
                **self.config,
            }
            a = WarehouseBigQueryAdapter(
                project=config.get("project"),
                location=config.get("location"),
                dataset=config.get("dataset", "datalake"),
                debug=self.debug,
            )
            self.datas[name] = a
            return a
        else:
            raise NotImplementedError(f"Adapter {name} not implemented")
