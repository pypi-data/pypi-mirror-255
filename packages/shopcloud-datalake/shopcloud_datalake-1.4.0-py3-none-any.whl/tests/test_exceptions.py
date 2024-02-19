import unittest

from shopcloud_datalake.exceptions import (CommandError, ConfigInvalidVersion,
                                           ConfigNotFound)


class TestExceptions(unittest.TestCase):
    def test_ConfigInvalidVersion(self):
        with self.assertRaises(ConfigInvalidVersion):
            raise ConfigInvalidVersion("Invalid version")

    def test_ConfigNotFound(self):
        with self.assertRaises(ConfigNotFound):
            raise ConfigNotFound("Config not found")

    def test_CommandError(self):
        with self.assertRaises(CommandError):
            raise CommandError("Command error")


if __name__ == "__main__":
    unittest.main()
