import unittest

from src.odoo_env_config.api import Env, OdooCliFlag
from src.odoo_env_config.section import ServerWideModuleConfigSection


class TestHttpOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = ServerWideModuleConfigSection()
        self.assertEqual(OdooCliFlag(), conf.to_values())
        self.assertListEqual([], conf.server_wide_modules)

    def test_serer_wide_modules_key(self):
        conf = ServerWideModuleConfigSection().init(Env({"SERVER_WIDE_MODULES": "module1,module2"}))
        self.assertEqual(["module1", "module2"], conf.server_wide_modules)
        conf = ServerWideModuleConfigSection().init(Env({"SERVER_WIDE_MODULES": "module1,module2,module1,base"}))
        # Assert no duplicate module and order is keeped
        self.assertEqual(["module1", "module2", "base"], conf.server_wide_modules)

    def test_module_name(self):
        conf = ServerWideModuleConfigSection().init(
            Env(
                {
                    "LOAD_MODULE_A": str(True),
                    "LOAD_MODULE_0": str(1),
                    "LOAD_MODULE_1": str(False),
                    "LOAD_MODULE_2": str(0),
                }
            )
        )
        # Assert "True" or "1" is valid activate value, and the sort is alpha
        self.assertEqual(["module_a", "module_0"], conf.server_wide_modules)
        conf = ServerWideModuleConfigSection().init(
            Env(
                {
                    "LOAD_QUEUE_JOB": "my_custom_module",
                }
            )
        )
        self.assertEqual(["my_custom_module"], conf.server_wide_modules)
        conf = ServerWideModuleConfigSection().init(
            Env(
                {
                    "LOAD_aslkaskalds": "queue_job",
                }
            )
        )
        self.assertEqual(["queue_job"], conf.server_wide_modules)
