import unittest

from src.odoo_env_config.api import Env, OdooCliFlag
from src.odoo_env_config.section.http_section import HttpOdooConfigSection


class TestHttpOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = HttpOdooConfigSection()
        self.assertEqual(OdooCliFlag({"no-http": True}), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertFalse(conf.enable)
        self.assertEqual(0, conf.longpolling_port)

    def test_disable(self):
        conf = HttpOdooConfigSection()
        conf.enable = True
        self.assertEqual(OdooCliFlag(), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertTrue(conf.enable)
        self.assertEqual(0, conf.longpolling_port)

    def test_global_http_key(self):
        conf = HttpOdooConfigSection().init(
            Env(
                {
                    "LONGPOLLING_PORT": "4040",
                    "HTTP_INTERFACE": "0.1.2.3",
                    "HTTP_PORT": "8080",
                    "HTTP_ENABLE": "True",
                }
            )
        )
        self.assertEqual("0.1.2.3", conf.interface)
        self.assertEqual(8080, conf.port)
        self.assertTrue(conf.enable)
        self.assertEqual(4040, conf.longpolling_port)
        self.assertDictEqual(
            OdooCliFlag({"longpolling-port": 4040, "http-port": 8080, "http-interface": "0.1.2.3"}), conf.to_values()
        )

    def test_enable(self):
        conf = HttpOdooConfigSection().init(
            Env(
                {
                    "HTTP_ENABLE": "True",
                }
            )
        )
        self.assertEqual(OdooCliFlag(), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertTrue(conf.enable)
        self.assertEqual(0, conf.longpolling_port)
        conf = HttpOdooConfigSection().init(
            Env(
                {
                    "HTTP_ENABLE": "False",
                }
            )
        )
        self.assertEqual(OdooCliFlag({"no-http": True}), conf.to_values())
        self.assertIsNone(conf.interface)
        self.assertEqual(0, conf.port)
        self.assertFalse(conf.enable)
        self.assertEqual(0, conf.longpolling_port)
