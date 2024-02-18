import unittest

from src.odoo_env_config.api import Env
from src.odoo_env_config.section import LoggerSection


class TestLogSection(unittest.TestCase):
    def test_default(self):
        conf = LoggerSection()
        self.assertIsNone(conf.logfile)
        self.assertIsNone(conf.log_handler)
        self.assertFalse(conf.log_request)
        self.assertFalse(conf.log_response)
        self.assertFalse(conf.log_web)
        self.assertFalse(conf.log_sql)
        self.assertFalse(conf.log_db)
        self.assertIsNone(conf.log_db_level)
        self.assertIsNone(conf.log_level)

    def test_global(self):
        conf = LoggerSection().init(
            Env(
                {
                    "LOGFILE": "logfile_value",
                    "LOG_HANDLER": "log_handler_value",
                    "LOG_REQUEST": str(True),
                    "LOG_RESPONSE": str(True),
                    "LOG_WEB": str(True),
                    "LOG_SQL": str(True),
                    "LOG_DB": str(True),
                    "LOG_DB_LEVEL": "log_db_level_value",
                    "LOG_LEVEL": "log_level_value",
                }
            )
        )
        self.assertEqual("logfile_value", conf.logfile)
        self.assertEqual("log_handler_value", conf.log_handler)
        self.assertTrue(conf.log_request)
        self.assertTrue(conf.log_response)
        self.assertTrue(conf.log_web)
        self.assertTrue(conf.log_sql)
        self.assertTrue(conf.log_db)
        self.assertEqual("log_db_level_value", conf.log_db_level)
        self.assertEqual("log_level_value", conf.log_level)

        flags = conf.to_values()
        self.assertIn("logfile", flags)
        self.assertEqual("logfile_value", flags["logfile"])
        self.assertIn("log-handler", flags)
        self.assertEqual("log_handler_value", flags["log-handler"])
        self.assertIn("log-request", flags)
        self.assertTrue(flags["log-request"])
        self.assertIn("log-response", flags)
        self.assertTrue(flags["log-request"])
        self.assertIn("log-web", flags)
        self.assertTrue(flags["log-web"])
        self.assertIn("log-sql", flags)
        self.assertTrue(flags["log-sql"])
        self.assertIn("log-db", flags)
        self.assertTrue(flags["log-db"])
        self.assertIn("log-db-level", flags)
        self.assertEqual("log_db_level_value", flags["log-db-level"])
        self.assertIn("log-level", flags)
        self.assertEqual("log_level_value", flags["log-level"])
