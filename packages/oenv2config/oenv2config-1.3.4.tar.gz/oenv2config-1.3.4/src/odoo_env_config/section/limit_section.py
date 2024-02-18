from typing_extensions import Self

from .. import api
from .worker_section import WorkersOdooConfigSection


class LimitOdooConfigSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.limit_request = 0
        self.limit_time_cpu = 0
        self.limit_time_real = 0
        self.osv_memory_count_limit = 0
        self.osv_memory_age_limit = 0
        self.limit_memory_hard = 0
        self.limit_memory_soft = 0

    def init(self, env: api.Env) -> Self:
        self.limit_request = env.get_int("LIMIT_REQUEST")
        self.limit_time_cpu = env.get_int("LIMIT_TIME_CPU")
        self.limit_time_real = env.get_int("LIMIT_TIME_REAL")
        self.osv_memory_count_limit = env.get_int("OSV_MEMORY_COUNT_LIMIT")
        self.osv_memory_age_limit = env.get_int("OSV_MEMORY_AGE_LIMIT")
        self.limit_memory_hard = env.get_int("LIMIT_MEMORY_HARD")
        self.limit_memory_soft = env.get_int("LIMIT_MEMORY_SOFT")

        if not self.limit_memory_hard or not self.limit_memory_soft:
            global_limit_memory_hard = env.get_int("GLOBAL_LIMIT_MEMORY_HARD")
            global_limit_memory_soft = env.get_int("GLOBAL_LIMIT_MEMORY_SOFT")
            nb_workers = WorkersOdooConfigSection().init(env).total or 1
            if not self.limit_memory_soft and global_limit_memory_soft:
                self.limit_memory_soft = global_limit_memory_soft // nb_workers
            if not self.limit_memory_hard and global_limit_memory_hard:
                self.limit_memory_hard = global_limit_memory_hard // nb_workers
        return self

    def to_values(self) -> api.OdooCliFlag:
        res = super().to_values()
        return res.set_all(
            {
                "limit-request": self.limit_request,
                "limit-time-cpu": self.limit_time_cpu,
                "limit-time-real": self.limit_time_real,
                "limit-memory-hard": self.limit_memory_hard,
                "limit-memory-soft": self.limit_memory_soft,
                "osv-memory-count-limit": self.osv_memory_count_limit,
                "osv-memory-age-limit": self.osv_memory_age_limit,
            }
        )
