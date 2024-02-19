import unittest
from datetime import date, datetime
from unittest.mock import Mock, patch

import pandas as pd

from shopcloud_datalake import erps, storages, tables, warehouses


class TestTableConfig(unittest.TestCase):
    def test_success(self):
        mock_storage_adapter = Mock(spec=storages.AbstractStorageAdapter)
        mock_storage_adapter.get.return_value = """
erp:
    adapter: sage
    table: TableKHKVKBelege
    order_by: BelID
warehouse:
    table: TableNameKHKVKBelege
partition:
  column: USER_CD
  type: DATE
"""
        config = tables.TableConfig.create_from_config("test", mock_storage_adapter)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.erp_adapter, "sage")
        self.assertEqual(config.erp_table, "TableKHKVKBelege")
        self.assertEqual(config.erp_order_by, "BelID")
        self.assertEqual(config.warehouse_table, "TableNameKHKVKBelege")
        self.assertEqual(config.partition_column, "USER_CD")
        self.assertEqual(config.partition_type, tables.PartitionType.DATE.value)

    def test_create_without_table_name_partioned(self):
        mock_storage_adapter = Mock(spec=storages.AbstractStorageAdapter)
        mock_storage_adapter.get.return_value = """
erp:
    adapter: sage
    table: TableKHKVKBelege
    order_by: BelID
partition:
  column: USER_CD
  type: DATE
"""
        config = tables.TableConfig.create_from_config("test", mock_storage_adapter)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.erp_adapter, "sage")
        self.assertEqual(config.erp_table, "TableKHKVKBelege")
        self.assertEqual(config.erp_order_by, "BelID")
        self.assertEqual(config.warehouse_table, None)
        self.assertEqual(config.partition_column, "USER_CD")
        self.assertEqual(config.partition_type, tables.PartitionType.DATE.value)

    def test_create_without_table_name(self):
        mock_storage_adapter = Mock(spec=storages.AbstractStorageAdapter)
        mock_storage_adapter.get.return_value = """
erp:
    adapter: sage
    table: KHKArtikel
    order_by: Artikelnummer
"""
        config = tables.TableConfig.create_from_config("test", mock_storage_adapter)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.erp_adapter, "sage")
        self.assertEqual(config.erp_table, "KHKArtikel")
        self.assertEqual(config.erp_order_by, "Artikelnummer")
        self.assertEqual(config.warehouse_table, None)
        self.assertEqual(config.partition_column, None)
        self.assertEqual(config.partition_type, None)

    def test_no_query_or_table(self):
        with self.assertRaises(ValueError):
            tables.TableConfig(
                name="test",
                erp_adapter="sage",
                erp_order_by="id",
                partition_column="date",
                partition_type=tables.PartitionType.DATE.value,
            )

    def test_invalid_adapter(self):
        with self.assertRaises(ValueError):
            tables.TableConfig(
                name="test",
                erp_adapter="invalid_adapter",
                erp_table="test_table",
                erp_query="SELECT * FROM test_table",
                erp_order_by="id",
                partition_column="date",
                partition_type=tables.PartitionType.DATE.value,
            )


class TestQuery(unittest.TestCase):
    def test_no_query_or_table(self):
        with self.assertRaises(ValueError):
            tables.Query()

    def test_has_partition(self):
        q = tables.Query(table="test", partition_column="date")
        self.assertTrue(q._has_partition)

    def test_to_table_sql_no_partition(self):
        q = tables.Query(table="test")
        self.assertEqual(q._to_table_sql(), "SELECT * FROM test")

    def test_to_table_sql_with_partition(self):
        q = tables.Query(
            table="test",
            partition_column="date",
            partition_type=tables.PartitionType.DATE.value,
            partition_date=date.today(),
        )
        expected_sql = f"SELECT * FROM KHKVKBelege WHERE date>='{date.today().strftime('%d.%m.%Y')} 00:00:00' AND date<='{date.today().strftime('%d.%m.%Y')} 23:59:59'"
        self.assertEqual(q._to_table_sql(), expected_sql)

    def test_to_query_sql_with_partition(self):
        q = tables.Query(
            query="SELECT * FROM test WHERE date='#PARTITION-DATE#'",
            partition_column="date",
            partition_type=tables.PartitionType.DATE.value,
            partition_date=date.today(),
        )
        expected_sql = f"SELECT * FROM test WHERE date='{date.today().strftime('%d.%m.%Y')}'"
        self.assertEqual(q._to_query_sql(), expected_sql)

    def test_to_sql_with_partition_missing_partition_date(self):
        q = tables.Query(
            table="test",
            partition_column="date",
            partition_type=tables.PartitionType.DATE.value,
        )
        with self.assertRaises(tables.QueryException):
            q.to_sql()

    def test_to_sql_from_query(self):
        q = tables.Query(query="SELECT * FROM test")
        expected_sql = "SELECT * FROM (SELECT * FROM test) AS data"
        self.assertEqual(q._to_query_sql(), expected_sql)
        self.assertEqual(q.to_sql(), expected_sql)

    def test_table_not_implemented_error(self):
        q = tables.Query(table="KHKVKBelege", partition_type="some_unsupported_type")
        with self.assertRaises(NotImplementedError) as e:
            q.to_sql()
            assert str(e.value) == "Partition type some_unsupported_type not implemented"

    def test_query_not_implemented_error(self):
        q = tables.Query(query="SELECT * FROM test", partition_type="some_unsupported_type")
        with self.assertRaises(NotImplementedError) as e:
            q.to_sql()
        self.assertEqual(str(e.exception), "Partition type some_unsupported_type not implemented")

    def test_query_partition_date_missing(self):
        q = tables.Query(query="SELECT * FROM test", partition_type=tables.PartitionType.DATE.value)
        with self.assertRaises(tables.QueryException) as e:
            q.to_sql()
        self.assertEqual(str(e.exception), "Partition date is required SELECT * FROM test")


class TestTablePartioned(unittest.TestCase):
    def setUp(self):
        self.mock_erp_adapter = Mock(spec=erps.AbstractErpAdapter)
        self.mock_warehouse_adapter = Mock(spec=warehouses.WarehouseAdapter)
        self.mock_storage_config = Mock(spec=storages.AbstractStorageAdapter)
        self.mock_storage_data = Mock(spec=storages.AbstractStorageAdapter)
        self.mock_storage_data.put_dataframe.return_value = "file_uri"
        self.mock_df = pd.DataFrame({"column1": [1, 2, 3, 4, 5, 6], "column2": [7, 8, 9, 10, 11, 12]})
        self.mock_erp_adapter.paginated.return_value = (self.mock_df, None)
        self.config = tables.TableConfig(
            name="test",
            erp_adapter="sage",
            erp_table="test_table",
            erp_query="SELECT * FROM test_table",
            erp_order_by="id",
            partition_column="date",
            partition_type=tables.PartitionType.DATE.value,
        )
        self.table = tables.Table(
            config=self.config,
            erp_adapter=self.mock_erp_adapter,
            warehouse_adapter=self.mock_warehouse_adapter,
            storage_config=self.mock_storage_config,
            storage_data=self.mock_storage_data,
        )

    def test_proceed(self):
        with patch("shopcloud_datalake.tables.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2022-01-01"
            self.table.proceed(debug=True, partition_date=datetime.now().date())
            self.assertEqual(self.table.total_rows, 6)
            self.mock_erp_adapter.paginated.assert_called_once()
            self.mock_storage_data.put_dataframe.assert_called_once()
            self.mock_warehouse_adapter.push.assert_called_once()
            self.assertEqual(self.table.stats.get('total_rows'), 6)


class TestTableUnPartioned(unittest.TestCase):
    def setUp(self):
        self.mock_erp_adapter = Mock(spec=erps.AbstractErpAdapter)
        self.mock_warehouse_adapter = Mock(spec=warehouses.WarehouseAdapter)
        self.mock_storage_config = Mock(spec=storages.AbstractStorageAdapter)
        self.mock_storage_data = Mock(spec=storages.AbstractStorageAdapter)
        self.mock_storage_data.put_dataframe.return_value = "file_uri"
        self.mock_df = pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})
        self.mock_erp_adapter.paginated.return_value = (self.mock_df, None)
        self.config = tables.TableConfig(
            name="test",
            erp_adapter="sage",
            erp_table="test_table",
            erp_query="SELECT * FROM test_table",
            erp_order_by="id",
            partition_column=None,
            partition_type=None,
        )
        self.table = tables.Table(
            config=self.config,
            erp_adapter=self.mock_erp_adapter,
            warehouse_adapter=self.mock_warehouse_adapter,
            storage_config=self.mock_storage_config,
            storage_data=self.mock_storage_data,
        )

    def test_proceed(self):
        with patch("shopcloud_datalake.tables.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2022-01-01"
            self.table.proceed(debug=True)
            self.assertEqual(self.table.total_rows, 3)
            self.mock_erp_adapter.paginated.assert_called_once()
            self.mock_storage_data.put_dataframe.assert_called_once()
            self.mock_warehouse_adapter.push.assert_called_once()
            self.assertEqual(self.table.stats.get('total_rows'), 3)


if __name__ == "__main__":
    unittest.main()
