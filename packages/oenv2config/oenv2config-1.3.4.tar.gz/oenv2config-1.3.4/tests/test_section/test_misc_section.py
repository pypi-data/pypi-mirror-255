import unittest

from src.odoo_env_config.api import Env
from src.odoo_env_config.section import MiscSection


class TestMiscSection(unittest.TestCase):
    def test_default(self):
        conf = MiscSection()
        self.assertFalse(conf.unaccent)
        self.assertEqual([], conf.without_demo)
        self.assertFalse(conf.stop_after_init)
        self.assertFalse(conf.save_config_file)

        flags = conf.to_values()
        self.assertFalse(flags)

    def test_global(self):
        conf = MiscSection().init(
            Env(
                {
                    "UNACCENT": str(True),
                    "WITHOUT_DEMO": "all,account",
                    "STOP_AFTER_INIT": str(True),
                    "SAVE_CONFIG_FILE": str(True),
                    "DATA_DIR": "data",
                }
            )
        )
        self.assertTrue(conf.unaccent)
        self.assertListEqual(["all", "account"], conf.without_demo)
        self.assertTrue(conf.stop_after_init)
        self.assertTrue(conf.save_config_file)

        flags = conf.to_values()
        self.assertIn("unaccent", flags)
        self.assertTrue(flags["unaccent"])

        self.assertIn("without-demo", flags)
        self.assertEqual("all,account", flags["without-demo"])

        self.assertIn("save", flags)
        self.assertTrue(flags["save"])

        self.assertIn("stop-after-init", flags)
        self.assertTrue(flags["stop-after-init"])

        self.assertIn("data-dir", flags)
        self.assertEqual(flags["data-dir"], "data")

    def test_datadir_sub_ODOO_PATH(self):
        conf = MiscSection().init(
            Env(
                {
                    "ODOO_PATH": "/odoo",
                    "DATA_DIR": "data",
                }
            )
        )
        self.assertEqual(conf.data_dir, "/odoo/data")
        flags = conf.to_values()
        self.assertIn("data-dir", flags)
        self.assertEqual(flags["data-dir"], "/odoo/data")

    def test_without_demo_FALSE(self):
        conf = MiscSection().init(
            Env(
                {
                    "WITHOUT_DEMO": "False",
                }
            )
        )
        self.assertFalse(conf.without_demo)
        flags = conf.to_values()
        self.assertNotIn("without-demo", flags)

    def test_without_demo_True(self):
        """
        Env WITHOUT_DEMO=True handle as --without-demo=all
        Returns:

        """
        conf = MiscSection().init(
            Env(
                {
                    "WITHOUT_DEMO": "True",
                }
            )
        )
        self.assertListEqual(["all"], conf.without_demo)
        flags = conf.to_values()
        self.assertIn("without-demo", flags)
        self.assertEqual("all", flags["without-demo"])
