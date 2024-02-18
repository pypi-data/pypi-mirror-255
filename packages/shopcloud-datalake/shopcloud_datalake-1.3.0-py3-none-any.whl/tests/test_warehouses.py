import json
import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from shopcloud_datalake import warehouses


@patch('shopcloud_datalake.warehouses.bigquery.Client')
class TestWarehouseBigQueryAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = warehouses.WarehouseBigQueryAdapter(
            project='test_project',
            location='test_location',
            dataset='test_dataset',
            debug=True
        )

    def test_push(self, mock_client):
        mock_load_job = MagicMock()
        mock_load_job.result.return_value = None
        mock_load_job.output_rows = 100
        mock_client.return_value.load_table_from_uri.return_value = mock_load_job

        self.adapter.push('test_name', 'test_uri')

    def test_push_with_dataset_not_found(self, mock_client):
        mock_load_job = MagicMock()
        mock_load_job.result.return_value = None
        mock_load_job.output_rows = 100
        mock_client.return_value.load_table_from_uri.return_value = mock_load_job
        mock_client.return_value.get_dataset.side_effect = NotFound('Not found')

        self.adapter.push('test_name', 'test_uri')

        mock_client.return_value.create_dataset.assert_called_once()


class TestWarehouseAdapterManager(unittest.TestCase):
    def test_get(self):
        mock_hub = MagicMock()
        mock_hub.read.side_effect = ["username", "password"]
        manager = warehouses.WarehouseManager(hub=MagicMock())
        adapter_a = manager.get(warehouses.WarehouseBigQueryAdapter.NAME)
        self.assertIsInstance(adapter_a, warehouses.WarehouseBigQueryAdapter)
        adapter_b = manager.get(warehouses.WarehouseBigQueryAdapter.NAME)
        self.assertIsInstance(adapter_b, warehouses.WarehouseBigQueryAdapter)
        self.assertEqual(adapter_a, adapter_b)

    def test_get_not_implemented(self):
        manager = warehouses.WarehouseManager(hub=MagicMock())
        with self.assertRaises(NotImplementedError):
            manager.get("not_implemented")
