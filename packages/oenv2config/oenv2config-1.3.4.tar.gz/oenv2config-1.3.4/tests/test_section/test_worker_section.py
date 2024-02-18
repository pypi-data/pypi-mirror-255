import unittest

from src.odoo_env_config.api import Env, OdooCliFlag, ServerUseCase
from src.odoo_env_config.section.worker_section import WorkersOdooConfigSection


class TestWorkersOdooConfigSection(unittest.TestCase):
    def test_default(self):
        conf = WorkersOdooConfigSection()
        self.assertEqual(0, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(0, conf.total)
        conf.init(Env())
        self.assertEqual(0, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(0, conf.total)
        self.assertFalse(conf.to_values())

    def test_WORKER_HTTP(self):
        conf = WorkersOdooConfigSection()
        self.assertEqual(0, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(0, conf.total)
        conf.init(Env({"WORKER_HTTP": str(10)}))
        self.assertEqual(10, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(10, conf.total)
        self.assertEqual(OdooCliFlag({"worker": 10}), conf.to_values())

    def test_WORKER_JOB(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "WORKER_JOB": str(2),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(0, conf.http)
        self.assertEqual(1, conf.cron)
        self.assertEqual(2, conf.job)
        self.assertEqual(3, conf.total)
        self.assertEqual(OdooCliFlag({"worker": 2, "max-cron-thread": 1}), conf.to_values())

    def test_priority(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                }
            )
        )
        self.assertEqual(2, conf.http)
        self.assertEqual(0, conf.cron)  # default value
        self.assertEqual(3, conf.job)
        self.assertEqual(5, conf.total)

    def test_usecase_worker(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "ODOO_USE_CASE": ServerUseCase.WORKER.value,
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(2, conf.http)
        self.assertEqual(1, conf.cron)
        self.assertEqual(3, conf.job)
        self.assertEqual(6, conf.total)
        self.assertEqual(OdooCliFlag({"worker": 5, "max-cron-thread": 1}), conf.to_values())

    def test_usecase_tests(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "ODOO_USE_CASE": ServerUseCase.TESTS.value,
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(0),
                }
            )
        )
        self.assertEqual(0, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(0, conf.total)
        self.assertEqual(OdooCliFlag(), conf.to_values())
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "TEST_ENABLE": str(True),
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(0),
                }
            )
        )
        self.assertEqual(0, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(0, conf.total)
        self.assertEqual(OdooCliFlag(), conf.to_values())

    def test_usecase_only_cron(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "ODOO_USE_CASE": ServerUseCase.ONLY_CRON.value,
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(2),
                }
            )
        )
        self.assertEqual(0, conf.http)
        self.assertEqual(2, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(2, conf.total)
        self.assertEqual(OdooCliFlag({"max-cron-thread": 2}), conf.to_values())

    def test_usecase_only_http(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "ODOO_USE_CASE": ServerUseCase.ONLY_HTTP.value,
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(2, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(2, conf.total)
        self.assertEqual(OdooCliFlag({"worker": 2}), conf.to_values())

    def test_usecase_only_job_runner(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "ODOO_USE_CASE": ServerUseCase.ONLY_JOB_RUNNER.value,
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(0, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(0, conf.total)
        self.assertEqual(OdooCliFlag(), conf.to_values())

    def test_usecase_only_job_worker(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "ODOO_USE_CASE": ServerUseCase.ONLY_JOB_WORKER.value,
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(0, conf.http)
        self.assertEqual(0, conf.cron)
        self.assertEqual(3, conf.job)
        self.assertEqual(3, conf.total)
        self.assertEqual(OdooCliFlag({"worker": 3}), conf.to_values())

    def test_usecase_threaded(self):
        conf = WorkersOdooConfigSection().init(
            Env(
                {
                    "ODOO_USE_CASE": ServerUseCase.THREADED_MODE.value,
                    "WORKER_HTTP": str(2),
                    "WORKER_JOB": str(3),
                    "WORKER_CRON": str(1),
                }
            )
        )
        self.assertEqual(0, conf.http)
        self.assertEqual(1, conf.cron)
        self.assertEqual(0, conf.job)
        self.assertEqual(1, conf.total)
        self.assertEqual(OdooCliFlag({"max-cron-thread": 1}), conf.to_values())
