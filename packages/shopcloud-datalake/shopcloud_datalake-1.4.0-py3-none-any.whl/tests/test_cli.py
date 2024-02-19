import argparse
import sys
import unittest
from unittest.mock import MagicMock, patch

from shopcloud_datalake import cli, helpers


class TestCli(unittest.TestCase):
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_no_args(self, mock_args):
        mock_args.return_value = argparse.Namespace(which=None, debug=False)
        with self.assertRaises(SystemExit) as cm:
            cli.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("sys.argv", ["cli"])
    def test_no_args(self):
        with self.assertRaises(SystemExit) as cm:
            cli.main()
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
