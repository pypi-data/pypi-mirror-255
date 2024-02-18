import shlex

import yaml
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog
from shopcloud_secrethub import SecretHub

from . import erps, helpers, steps, storages, tables, warehouses


def action_sync(**kwargs) -> int:
    debug = kwargs.get("debug", False)
    is_simulate = kwargs.get("is_simulate", False)
    hub = SecretHub(user_app="shopcloud-datalake")

    project = kwargs.get("project")
    location = kwargs.get("location")

    storage_adapter_manager = storages.StorageAdapterManager(
        hub,
        debug=debug,
        config={
            "project": project,
            "location": location,
        }
    )
    bucket_config = storage_adapter_manager.get(storages.GoogleCloudStorageAdapter.NAME, bucket_type="config")
    base_dir = kwargs.get("base_dir")
    if base_dir is None:
        base_dir = "./"
    else:
        base_dir = f"./{base_dir}"
    manager = steps.Manager({}, [
        steps.StepCommand(
            shlex.split(
                f'gsutil -m rsync -r -u {base_dir} "{bucket_config}"',
            ),
            is_async=False,
        ),
    ], simulate=is_simulate)
    rc = manager.run()
    if rc != 0:
        return rc
    print(helpers.bcolors.OKGREEN + 'Sync Config to storage' + helpers.bcolors.ENDC)
    return 0


def action_create(**kwargs) -> int:
    def erp_config() -> dict:
        adapter = radiolist_dialog(
            title="ERP Configuration",
            text="Please choose the adapter:",
            values=[
                (erps.SageAdapter.NAME, "Sage"),
            ],
        ).run()

        table = input_dialog(
            title="ERP Configuration",
            text="Please enter the table:",
        ).run()

        order_by = input_dialog(
            title="ERP Configuration",
            text="Please enter the order by:",
        ).run()

        has_partition = radiolist_dialog(
            title="ERP Configuration",
            text="Does it have a partition?",
            values=[
                ("True", "Yes"),
                ("False", "No"),
            ],
        ).run()
        has_partition = has_partition == "True"

        if not has_partition:
            return {
                "adapter": adapter,
                "table": table,
                "order_by": order_by,
            }

        partition_type = radiolist_dialog(
            title="ERP Configuration",
            text="Partition Type:",
            values=[
                (tables.PartitionType.DATE.value, tables.PartitionType.DATE.value),
            ],
        ).run()

        partition_column = input_dialog(
            title="ERP Configuration",
            text="Please enter the partition column:",
        ).run()

        return {
            "adapter": adapter,
            "table": table,
            "order_by": order_by,
            "has_partition": has_partition,
            "partition_column": partition_column,
            "partition_type": partition_type,
        }

    def warehouse_config(erp: dict) -> dict:
        adapter = radiolist_dialog(
            title="Warehouse Configuration",
            text="Please choose the adapter:",
            values=[
                (warehouses.WarehouseBigQueryAdapter.NAME, "BigQuery"),
            ],
        ).run()

        table = input_dialog(
            title="Warehouse Configuration",
            text="The Name of the Table to create:",
            default=f"{erp.get('table')}",
        ).run()

        return {
            "adapter": adapter,
            "table": table,
        }

    erp = erp_config()
    warehouse = warehouse_config(erp)

    base_dir = kwargs.get("base_dir")
    if base_dir is None:
        base_dir = "."

    with open(f'{base_dir}/{erp.get("table").lower()}.yaml', "w") as file:
        data = {
            "erp": {
                "adapter": erp.get("adapter"),
                "table": erp.get("table"),
                "order_by": erp.get("order_by"),
            },
            "warehouse": {
                "adapter": warehouse.get("adapter"),
                "table": warehouse.get("table"),
            },
        }
        if erp.get("has_partition"):
            partition = {
                "column": erp.get("partition_column"),
                "type": erp.get("partition_type"),
            }
            data["partition"] = partition
        yaml.dump(data, file)

    return 0

    return 0


def main(**kwargs) -> int:
    action = kwargs.get("action")
    print(kwargs)
    if action == "sync":
        return action_sync(**kwargs)
    elif action == "create":
        return action_create(**kwargs)
    else:
        print("Unknown action")
        return 1
    pass
