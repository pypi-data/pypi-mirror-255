import unittest

from src.odoo_env_config.api import Env
from src.odoo_env_config.section import UpdateInstallSection
from tests._decorators import MultiOdooVersion


class TestUpdateInitSection(unittest.TestCase):
    @MultiOdooVersion.without_args
    def test_default(self):
        conf = UpdateInstallSection()
        self.assertEqual([], conf.install)
        self.assertEqual([], conf.update)
        flags = conf.to_values()
        self.assertFalse(flags)

    @MultiOdooVersion.with_args
    def test_value(self, version: int):
        conf = UpdateInstallSection().init(
            Env(
                {
                    "ODOO_VERSION": str(version),
                    "INSTALL": " module1 , module2, module3 , module1 ",
                    "UPDATE": " module_a , module_b , module_c, module_b ",
                }
            )
        )
        flags = conf.to_values()

        self.assertListEqual(["module1", "module2", "module3"], conf.install)
        self.assertIn("init", flags)
        self.assertEqual("module1,module2,module3", flags["init"])

        self.assertListEqual(["module_a", "module_b", "module_c"], conf.update)
        self.assertIn("update", flags)
        self.assertEqual("module_a,module_b,module_c", flags["update"])
