import unittest
from unittest.mock import Mock

from shopcloud_datalake.managers import AbstractAdapterManager


class Manager(AbstractAdapterManager):
    def get(self, name):
        return self.datas.get(name)


class TestAdapterManager(unittest.TestCase):
    def setUp(self):
        self.mock_hub = Mock()
        self.manager = Manager(
            self.mock_hub, config={"key": "value"}, debug=True
        )

    def test_init(self):
        self.assertEqual(self.manager.hub, self.mock_hub)
        self.assertEqual(self.manager.datas, {})
        self.assertEqual(self.manager.config, {"key": "value"})
        self.assertEqual(self.manager.debug, True)

    def test_register(self):
        mock_adapter = Mock()
        self.manager.register("test", mock_adapter)
        self.assertEqual(self.manager.datas, {"test": mock_adapter})

    def test_get(self):
        self.manager.get("test")


if __name__ == "__main__":
    unittest.main()
