from typing_extensions import Self

from .. import api
from .test_section import TestOdooConfigSection


class WorkersOdooConfigSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.http: int = 0
        self.cron: int = 0
        self.job: int = 0
        self.odoo_use_case: api.ServerUseCase = api.ServerUseCase.WORKER
        self._force_set_cron: bool = False

    def init(self, env: api.Env) -> Self:
        self.odoo_use_case = env.get_enum("ODOO_USE_CASE", api.ServerUseCase, default=api.ServerUseCase.WORKER)
        if TestOdooConfigSection().init(env).enable:
            self.odoo_use_case = api.ServerUseCase.TESTS

        if self.odoo_use_case == api.ServerUseCase.WORKER:
            self.cron = env.get_int("WORKER_CRON")
            self.job = env.get_int("WORKER_JOB")
            self.http = env.get_int("WORKER_HTTP")
        elif self.odoo_use_case == api.ServerUseCase.THREADED_MODE:
            self.cron = env.get_int("WORKER_CRON")
        elif self.odoo_use_case == api.ServerUseCase.ONLY_JOB_WORKER:
            self.job = env.get_int("WORKER_JOB")
        elif self.odoo_use_case == api.ServerUseCase.ONLY_HTTP:
            self.http = env.get_int("WORKER_HTTP")
        elif self.odoo_use_case == api.ServerUseCase.ONLY_CRON:
            self.cron = env.get_int("WORKER_CRON")
        else:
            # api.ServerUseCase.TESTS
            # api.ServerUseCase.ONLY_JOB_RUNNER
            self.http = self.cron = self.job = 0

        self._force_set_cron = not env.main_instance and self.odoo_use_case != api.ServerUseCase.ONLY_CRON
        # In case not mail instance, then we don't want to have cron again, only on the main instance
        if self._force_set_cron:
            self.cron = 0

        return self

    @property
    def total(self):
        return self.worker + self.cron

    @property
    def worker(self):
        return self.http + self.job

    def to_values(self) -> api.OdooCliFlag:
        res = super().to_values()
        res.set("worker", self.worker)
        if self.odoo_use_case in (
            api.ServerUseCase.ONLY_CRON,
            api.ServerUseCase.WORKER,
            api.ServerUseCase.THREADED_MODE,
        ):
            res.set("max-cron-thread", self.cron, force_set=self._force_set_cron)
        return res
