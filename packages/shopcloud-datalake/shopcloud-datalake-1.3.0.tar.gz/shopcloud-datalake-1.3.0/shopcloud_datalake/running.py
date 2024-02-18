from datetime import datetime, timedelta
from typing import Generator, List

from shopcloud_secrethub import SecretHub

from . import erps, helpers, storages, tables, warehouses


def main(**kwargs) -> int:
    debug = kwargs.get("debug", False)
    hub = SecretHub(user_app="shopcloud-datalake")

    project = kwargs.get("project")
    location = kwargs.get("location")
    raise_exception = kwargs.get("raise_exception", False)

    partition_date = kwargs.get("partition_date")
    history_days = kwargs.get("history_days")
    partition_dates = (
        [partition_date]
        if partition_date
        else [
            (datetime.now().date() - timedelta(days=i))
            for i in range(history_days or 0)
        ]
    )

    storage_adapter_manager = storages.StorageAdapterManager(
        hub,
        debug=debug,
        config={
            "project": project,
            "location": location,
        },
    )
    bucket_data = storage_adapter_manager.get(
        storages.GoogleCloudStorageAdapter.NAME, bucket_type="data"
    )
    bucket_config = storage_adapter_manager.get(
        storages.GoogleCloudStorageAdapter.NAME, bucket_type="config"
    )

    table = kwargs.get("table")
    datas = (
        [table]
        if table is not None
        else [
            x.replace(".yaml", "") for x in bucket_config.list() if x.endswith(".yaml")
        ]
    )
    datas = [
        helpers.Pipeline(name="table-loading", _for=x, raise_exception=raise_exception)
        for x in datas
    ]
    datas = [
        x.step(
            "table:load-config",
            lambda y: tables.TableConfig.create_from_config(y._for, bucket_config),
        )
        for x in datas
    ]

    erp_adapter_manager = erps.ErpAdapterManager(
        hub,
        debug=debug,
        config={
            "request_page_limit": kwargs.get("request_page_limit", 5000),
            "max_workers": kwargs.get("max_workers", 4),
        },
    )
    warehouse_adapter_manager = warehouses.WarehouseManager(
        hub,
        debug=debug,
        config={
            "project": project,
            "location": location,
        },
    )
    datas = [
        x.step(
            "table:init",
            lambda y: tables.Table(
                config=y.data,
                erp_adapter=erp_adapter_manager.get(y.data.erp_adapter),
                warehouse_adapter=warehouse_adapter_manager.get(
                    warehouses.WarehouseBigQueryAdapter.NAME
                ),
                storage_data=bucket_data,
                storage_config=bucket_config,
            ),
        )
        for x in datas
    ]

    def generate_partitons(
        pipeline: helpers.Pipeline, partition_dates: List[datetime.date]
    ) -> Generator[helpers.Pipeline, None, None]:
        if pipeline.is_success is False:
            yield pipeline
            return None

        if pipeline.data.config.partition_column is not None:
            for d in partition_dates:
                p = helpers.Pipeline.create_from(pipeline)
                p.partition = d
                yield p

            return None

        yield pipeline

    datas = [generate_partitons(x, partition_dates) for x in datas]
    datas = [x for y in datas for x in y]
    datas = [
        x.step(
            "table:proceed",
            lambda y, current_x=x: current_x.data.proceed(
                debug=debug, partition_date=current_x.partition
            ),
        )
        for x in datas
    ]

    for p in datas:
        if p.is_success:
            print(
                helpers.bcolors.OKGREEN
                + f"+ {p.name} {p._for} {p.partition} {p.data.stats}"
                + helpers.bcolors.ENDC
            )
        else:
            print(
                helpers.bcolors.FAIL
                + f"+ {p.name} {p._for} {p.partition} {p.steps[-1]['exception']}"
                + helpers.bcolors.ENDC
            )

    return 0
