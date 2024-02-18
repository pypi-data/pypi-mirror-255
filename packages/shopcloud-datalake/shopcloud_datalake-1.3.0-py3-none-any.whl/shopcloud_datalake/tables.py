import time
from dataclasses import Field, dataclass, field
from datetime import date, datetime
from enum import Enum
from functools import wraps
from typing import Optional

import pandas as pd
import yaml

from . import erps, storages, warehouses


def retry(retries=3, delay=10):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Retrying {func.__name__} {func.__class__.__name__} {i + 1}/{retries} {e}")
                    if i < retries - 1:
                        time.sleep(delay)
                    else:
                        raise  # re-raise the last exception

        return wrapper

    return decorator


class PartitionType(Enum):
    DATE = "DATE"


@dataclass
class TableConfig:
    name: str
    erp_adapter: str
    erp_order_by: str = field(metadata={"validate": lambda x: x if x != "" else None})
    erp_query: Optional[str] = field(
        default=None, metadata={"validate": lambda x: x if x != "" else None}
    )
    erp_table: Optional[str] = field(
        default=None, metadata={"validate": lambda x: x if x != "" else None}
    )
    warehouse_table: Optional[str] = field(
        default=None, metadata={"validate": lambda x: x if x != "" else None}
    )
    partition_column: str = None
    partition_type: Optional[str] = field(
        default=None,
        metadata={
            "validate": lambda x: x
            if x not in [PartitionType.DATE.value]
            else ValueError("'partition_type' can only be Date.")
        },
    )

    def __post_init__(self):
        errors = []
        if not self.erp_query and not self.erp_table:
            errors.append(
                {
                    "fields": ["erp_query", "erp_table"],
                    "message": "Either 'erp_query' or 'erp_table' must be set.",
                }
            )
        if self.erp_adapter not in [erps.SageAdapter.NAME]:
            errors.append(
                {
                    "fields": ["erp_adapter"],
                    "message": f"'{self.erp_adapter}' is not a valid erp_adapter.",
                }
            )
        if len(errors) > 0:
            raise ValueError(errors)
        for field_name, field_def in self.__annotations__.items():
            if isinstance(field_def, Field):
                validator = field_def.metadata.get("validate")
                if validator:
                    setattr(self, field_name, validator(getattr(self, field_name)))

    @staticmethod
    def create_from_config(
        name: str, bucket: storages.AbstractStorageAdapter, **kwargs
    ) -> "TableConfig":
        data = bucket.get(f"{name.lower()}.yaml")
        data = yaml.load(data, Loader=yaml.SafeLoader)
        return TableConfig(
            name=name,
            erp_adapter=data.get("erp", {}).get("adapter"),
            erp_table=data.get("erp", {}).get("table"),
            erp_query=data.get("erp", {}).get("query"),
            erp_order_by=data.get("erp", {}).get("order_by"),
            warehouse_table=data.get("warehouse", {}).get("table"),
            partition_column=data.get("partition", {}).get("column"),
            partition_type=data.get("partition", {}).get("type"),
        )


class QueryException(Exception):
    pass


@dataclass
class Query:
    table: str = None
    query: str = None
    order_by: str = None
    _has_partition: bool = False
    partition_column: Optional[str] = None
    partition_type: Optional[str] = None
    partition_date: Optional[date] = None

    def __post_init__(self):
        errors = []
        if not self.query and not self.table:
            errors.append(
                {
                    "fields": ["query", "table"],
                    "message": "Either 'query' or 'table' must be set.",
                }
            )
        if len(errors) > 0:
            raise ValueError(errors)
        self._has_partition = bool(self.partition_column or self.partition_type)

    def _to_table_sql(self, **kwargs) -> str:
        if not self._has_partition:
            return f"SELECT * FROM {self.table}"
        if self.partition_type == PartitionType.DATE.value:
            if self.partition_date is None:
                raise QueryException(f"Partition date is required {self.table}")
            return f"SELECT * FROM KHKVKBelege WHERE {self.partition_column}>='{self.partition_date.strftime('%d.%m.%Y')} 00:00:00' AND {self.partition_column}<='{self.partition_date.strftime('%d.%m.%Y')} 23:59:59'"
        else:
            raise NotImplementedError(
                f"Partition type {self.partition_type} not implemented"
            )

    def _to_query_sql(self, **kwargs) -> str:
        if not self._has_partition:
            return f"SELECT * FROM ({self.query}) AS data"
        if self.partition_type == PartitionType.DATE.value:
            if self.partition_date is None:
                raise QueryException(f"Partition date is required {self.query}")
            return f"{self.query}".replace(
                "#PARTITION-DATE#", self.partition_date.strftime("%d.%m.%Y")
            )
        else:
            raise NotImplementedError(
                f"Partition type {self.partition_type} not implemented"
            )

    def to_sql(self, **kwargs) -> str:
        if self.table is not None:
            return self._to_table_sql()
        else:
            return self._to_query_sql()


@dataclass
class Table:
    config: TableConfig
    erp_adapter: erps.AbstractErpAdapter
    warehouse_adapter: warehouses.WarehouseAdapter
    storage_config: storages.AbstractStorageAdapter
    storage_data: storages.AbstractStorageAdapter
    data: pd.DataFrame = None
    total_rows: int = 0
    total_columns: int = 0

    @retry(retries=3, delay=10)
    def proceed(self, **kwargs):
        print(f'+ [{self.__class__.__name__}] {self.config.name} - start processing')
        debug = kwargs.get("debug", False)
        partition_date = kwargs.get("partition_date", None)

        # fetch-data
        q = Query(
            table=self.config.erp_table,
            query=self.config.erp_query,
            order_by=self.config.erp_order_by,
            partition_column=self.config.partition_column,
            partition_type=self.config.partition_type,
            partition_date=partition_date,
        )
        self.data, _ = self.erp_adapter.paginated(
            query=q.to_sql(),
            order_by=q.order_by,
        )
        self.total_rows = self.data.shape[0]
        self.total_columns = self.data.shape[1]
        self.data["CreatedAt"] = datetime.now().strftime("%Y-%m-%d")
        # push to datalake
        if self.config.partition_type == PartitionType.DATE.value:
            file_uri = self.storage_data.put_dataframe(
                f"{partition_date.strftime('%Y')}/{partition_date.strftime('%m')}/{partition_date.strftime('%d')}/{self.config.name}",
                self.data,
            )
        else:
            file_uri = self.storage_data.put_dataframe(
                f"{self.config.name}",
                self.data,
            )
        # push to warehouse
        if debug:
            print(
                "Partition Column", self.config.partition_type, PartitionType.DATE.value
            )
        table_name = (
            self.config.warehouse_table
            if self.config.warehouse_table
            else self.config.name
        )
        if self.config.partition_type == PartitionType.DATE.value:
            table_name = f"{self.config.name}_{partition_date.strftime('%Y%m%d')}"
        self.warehouse_adapter.push(table_name, file_uri)
        return self

    @property
    def stats(self) -> dict:
        return {
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
        }
