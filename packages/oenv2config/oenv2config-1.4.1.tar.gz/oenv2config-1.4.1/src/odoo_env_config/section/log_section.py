from typing_extensions import Self

from .. import api


class LoggerSection(api.EnvConfigSection):
    def __init__(self) -> None:
        super().__init__()
        self.logfile = None
        self.log_handler = None
        self.log_request = False
        self.log_response = False
        self.log_web = False
        self.log_sql = False
        self.log_db = False
        self.log_db_level = None
        self.log_level = None

    def init(self, curr_env: api.Env) -> Self:
        self.logfile = curr_env.get("LOGFILE")
        self.log_handler = curr_env.get("LOG_HANDLER")
        self.log_request = curr_env.get_bool("LOG_REQUEST")
        self.log_response = curr_env.get_bool("LOG_RESPONSE")
        self.log_web = curr_env.get_bool("LOG_WEB")
        self.log_sql = curr_env.get_bool("LOG_SQL")
        self.log_db = curr_env.get_bool("LOG_DB")
        self.log_db_level = curr_env.get("LOG_DB_LEVEL")
        self.log_level = curr_env.get("LOG_LEVEL")
        return self

    def to_values(self) -> api.OdooCliFlag:
        flags = super().to_values()
        flags.set("logfile", self.logfile)
        flags.set("log-handler", self.log_handler)
        flags.set("log-request", self.log_request)
        flags.set("log-response", self.log_response)
        flags.set("log-web", self.log_web)
        flags.set("log-sql", self.log_sql)
        flags.set("log-db", self.log_db)
        flags.set("log-db-level", self.log_db_level)
        flags.set("log-level", self.log_level)
        return flags
