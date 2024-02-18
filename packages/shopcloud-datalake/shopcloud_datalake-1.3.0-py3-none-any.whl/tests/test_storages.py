import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

from shopcloud_datalake import storages


class TestGoogleCloudStorageAdapter(unittest.TestCase):
    @patch("google.cloud.storage.Client")
    def test_init(self, mock_client):
        mock_bucket = Mock()
        mock_client.return_value.get_bucket.return_value = mock_bucket
        adapter = storages.GoogleCloudStorageAdapter("project", "name")
        self.assertEqual(adapter.project, "project")
        self.assertEqual(adapter.name, "name")

    @patch("google.cloud.storage.Client")
    def test_get_or_create_bucket(self, mock_client):
        mock_bucket = Mock()
        mock_client.return_value.get_bucket.return_value = mock_bucket
        storages.GoogleCloudStorageAdapter("project", "name")
        mock_client.return_value.get_bucket.assert_called_once_with("name")

    @patch("google.cloud.storage.Client")
    def test_get_or_create_bucket_exception(self, mock_client):
        mock_bucket = Mock()
        mock_client.return_value.get_bucket.side_effect = Exception("Bucket not found")
        mock_client.return_value.bucket.return_value = mock_bucket
        adapter = storages.GoogleCloudStorageAdapter("project", "name")
        mock_client.return_value.create_bucket.assert_called_once_with(
            adapter._bucket, project="project"
        )

    @patch("google.cloud.storage.Client")
    def test_list(self, mock_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.name = "blob_name"
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_client.return_value.get_bucket.return_value = mock_bucket
        adapter = storages.GoogleCloudStorageAdapter("project", "name")
        blobs = adapter.list("/")
        self.assertEqual(blobs, ["blob_name"])

    @patch("google.cloud.storage.Client")
    def test_get(self, mock_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.download_as_string.return_value = b"content"
        mock_bucket.blob.return_value = mock_blob
        mock_client.return_value.get_bucket.return_value = mock_bucket
        adapter = storages.GoogleCloudStorageAdapter("project", "name")
        content = adapter.get("path")
        self.assertEqual(content, "content")

    @patch("google.cloud.storage.Client")
    def test_put(self, mock_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.return_value.get_bucket.return_value = mock_bucket
        adapter = storages.GoogleCloudStorageAdapter("project", "name")
        path = adapter.put("path", "content")
        mock_blob.upload_from_string.assert_called_once_with("content")
        self.assertEqual(path, "gs://name/path")

    @patch("google.cloud.storage.Client")
    def test_put_dataframe(self, mock_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.return_value.get_bucket.return_value = mock_bucket
        adapter = storages.GoogleCloudStorageAdapter("project", "name")
        path = adapter.put_dataframe("path", pd.DataFrame([1, 2, 3]))
        mock_blob.upload_from_filename.assert_called_once()
        self.assertEqual(path, "gs://name/path.parquet")

    @patch("google.cloud.storage.Client")
    def test_delete(self, mock_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.return_value.get_bucket.return_value = mock_bucket
        adapter = storages.GoogleCloudStorageAdapter("project", "name")
        adapter.delete("path")
        mock_blob.delete.assert_called_once()


class TestStorageAdapterManager(unittest.TestCase):
    @patch("google.cloud.storage.Client")
    def test_get(self, mock_client):
        mock_bucket = Mock()
        mock_client.return_value.get_bucket.return_value = mock_bucket
        manager = storages.StorageAdapterManager(hub=MagicMock())
        adapter_a = manager.get(storages.GoogleCloudStorageAdapter.NAME)
        self.assertIsInstance(adapter_a, storages.GoogleCloudStorageAdapter)
        adapter_b = manager.get(storages.GoogleCloudStorageAdapter.NAME)
        self.assertIsInstance(adapter_b, storages.GoogleCloudStorageAdapter)
        self.assertEqual(adapter_a, adapter_b)

    def test_get_not_implemented(self):
        manager = storages.StorageAdapterManager(hub=MagicMock())
        with self.assertRaises(NotImplementedError):
            manager.get("not_implemented")


if __name__ == "__main__":
    unittest.main()
