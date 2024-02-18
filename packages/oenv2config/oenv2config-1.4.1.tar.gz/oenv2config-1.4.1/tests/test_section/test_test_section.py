import unittest

from src.odoo_env_config.api import Env
from src.odoo_env_config.section import TestOdooConfigSection
from tests._decorators import MultiOdooVersion


class TestTestSection(unittest.TestCase):
    @MultiOdooVersion.without_args
    def test_default(self):
        conf = TestOdooConfigSection()
        self.assertFalse(conf.enable)
        self.assertIsNone(conf.test_tags)
        self.assertIsNone(conf.test_file)

        flags = conf.to_values()
        self.assertFalse(flags)

    @MultiOdooVersion.with_args
    def test_version_disable(self, version: int):
        conf = TestOdooConfigSection().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "TEST_ENABLE": str(False),
                    "TEST_TAGS": "test_tags_value",
                    "TEST_FILE": "test_file_value",
                }
            )
        )
        flags = conf.to_values()
        self.assertFalse(conf.enable)
        self.assertFalse(flags)

    @MultiOdooVersion.with_args
    def test_odoo_test_tags(self, version: int):
        conf = TestOdooConfigSection().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "TEST_ENABLE": str(True),
                    "TEST_TAGS": "test_tags_value",
                    "TEST_FILE": "test_file_value",
                }
            )
        )
        flags = conf.to_values()

        self.assertTrue(conf.enable)
        self.assertIn("test-enable", flags)
        self.assertTrue(flags["test-enable"])

        # test-tags not supported in Odoo 11 or less
        if version > 11:
            self.assertIn("test-tags", flags)
            self.assertEqual("test_tags_value", flags["test-tags"])
        else:
            self.assertNotIn("test-tags", flags)

        self.assertEqual("test_file_value", conf.test_file)
        self.assertIn("test-file", flags)
        self.assertEqual("test_file_value", flags["test-file"])
