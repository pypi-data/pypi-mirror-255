import json
import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pandas as pd

from shopcloud_datalake import erps


@dataclass
class Response:
    status_code: int = 200
    text: str = "Test"

    def json(self):
        return json.loads(self.text)

    @property
    def content(self) -> bytes:
        return self.text.encode("utf-8")


class TestErpAdapterManager(unittest.TestCase):
    def test_get(self):
        mock_hub = MagicMock()
        mock_hub.read.side_effect = ["username", "password"]
        manager = erps.ErpAdapterManager(hub=MagicMock())
        adapter_a = manager.get(erps.SageAdapter.NAME)
        self.assertIsInstance(adapter_a, erps.SageAdapter)
        adapter_b = manager.get(erps.SageAdapter.NAME)
        self.assertIsInstance(adapter_b, erps.SageAdapter)
        self.assertEqual(adapter_a, adapter_b)

    def test_get_not_implemented(self):
        manager = erps.ErpAdapterManager(hub=MagicMock())
        with self.assertRaises(NotImplementedError):
            manager.get("not_implemented")


class TestSageAdapter(unittest.TestCase):
    @patch("requests.post")
    def test_fetch(self, mock_post):
        mock_post.return_value = Response(status_code=200, text="Total\n10")

        adapter = erps.SageAdapter("endpoint", "api_token")
        query = "SELECT * FROM table"
        result = adapter.fetch(query)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)

    @patch("requests.post")
    def test_fetch_api_error(self, mock_post):
        mock_post.return_value = Response(status_code=400, text="Bad Request")

        adapter = erps.SageAdapter("endpoint", "api_token")
        query = "SELECT * FROM table"
        with self.assertRaises(erps.APIError):
            adapter.fetch(query)

        r = erps.APIError(Response(status_code=400, text="Bad Request"))
        r.__repr__()

    @patch("requests.post")
    def test_fetch_api_sql_error(self, mock_post):
        mock_post.return_value = Response(
            status_code=200, text=json.dumps({"error": "SQL Error"})
        )

        adapter = erps.SageAdapter("endpoint", "api_token")
        query = "SELECT * FROM table"
        with self.assertRaises(erps.SQLError):
            adapter.fetch(query)

    @patch("requests.post")
    def test_paginated(self, mock_post):
        responses = [
            Response(status_code=200, text="total\n10"),
            Response(status_code=200, text="A,B,C\n1,2,3\n4,5,6"),
        ]
        mock_post.side_effect = responses

        adapter = erps.SageAdapter("endpoint", "api_token")
        query = "SELECT * FROM table"
        result, total = adapter.paginated(query, "ByColumn")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(mock_post.call_count, len(responses))

    @patch("requests.post")
    def test_paginated_empty(self, mock_post):
        responses = [
            Response(status_code=200, text=""),
        ]
        mock_post.side_effect = responses

        adapter = erps.SageAdapter("endpoint", "api_token")
        query = "SELECT * FROM table"
        result, total = adapter.paginated(query, "ByColumn")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(mock_post.call_count, len(responses))


if __name__ == "__main__":
    unittest.main()
