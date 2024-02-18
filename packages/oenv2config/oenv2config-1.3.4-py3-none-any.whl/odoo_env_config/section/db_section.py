"""
Contains de converter from [os.environ][os.environ] wrapper in
[][odoo_env_config.api.Env] in this library to valid `odoo.tools.config` options
"""
from __future__ import annotations

import enum
from typing import Union

from typing_extensions import Self

from .. import api
from .worker_section import WorkersOdooConfigSection as _WorkersOdooConfigSection


class MaxConnMode(enum.Enum):
    """
    Mode to compute the max_conn attribute
    Attributes:
        AUTO: the max_conn is compute from the number of worker defined
        in [`WorkerConfig`][odoo_env_config.section.worker_section]
        FIXED: the value is taken from `"DB_MAX_CONN"` is [][os.environ]
    """

    AUTO = "AUTO"
    FIXED = "FIXED"


class DatabaseOdooConfigSection(api.EnvConfigSection):
    """
    A dataclass to hold the database Odoo config group option

    Attributes:
        name: Name of the database
        host: The URI of the postgresql service get from `"DB_HOST"` in
        user: The URI of the postgresql service get from `"DB_HOST"` in
        port: The URI of the postgresql service get from `"DB_HOST"` in
        password: The URI of the postgresql service get from `"DB_HOST"` in
        max_conn: The URI of the postgresql service get from `"DB_HOST"` in
        filter: The URI of the postgresql service get from `"DB_HOST"` in
        log_enable: The URI of the postgresql service get from `"DB_HOST"` in
        log_level: The URI of the postgresql service get from `"DB_HOST"` in
        show: The URI of the postgresql service get from `"DB_HOST"` in
        maxconn_mode: The URI of the postgresql service get from `"DB_HOST"` in
    """

    def __init__(self):
        super().__init__()
        self.name: Union[str, None] = None
        self.host: Union[str, None] = None
        self.port: int = 0
        self.user: Union[str, None] = None
        self.password: Union[str, None] = None
        self.max_conn: int = 0
        self.filter: Union[str, None] = None
        self.log_level: Union[str, None] = None
        self.log_enable: bool = False
        self.show: bool = True
        self.maxconn_mode: MaxConnMode = MaxConnMode.AUTO

    def init(self, curr_env: api.Env) -> Self:
        """
        Args:
            curr_env: The current env to parse
        Returns:
            A new `DatabaseOdooConfigSection`
        """

        self.name = curr_env.get("DB_NAME")
        self.host = curr_env.get("DB_HOST")
        self.port = curr_env.get_int("DB_PORT")
        self.user = curr_env.get("DB_USER")
        self.password = curr_env.get("DB_PASSWORD")
        self.max_conn = curr_env.get_int("DB_MAX_CONN")
        self.filter = curr_env.get("DB_FILTER")
        self.log_enable = curr_env.get_bool("LOG_DB")
        self.log_level = curr_env.get("LOG_DB_LEVEL")
        self.show = curr_env.get_bool("LIST_DB", default=True)
        # Determine max_conn
        self.maxconn_mode = curr_env.get_enum("DB_MAX_CONN_MODE", MaxConnMode, default=MaxConnMode.FIXED)
        if self.maxconn_mode == MaxConnMode.AUTO:
            self.max_conn = max(self.max_conn, self.compute_auto_maxconn(curr_env))

        if not self.filter and not self.show:
            self.filter = self.name
        return self

    def to_values(self) -> api.OdooCliFlag:
        res = super().to_values()
        res.set_all(
            {
                "db_host": self.host,
                "db_port": self.port,
                "db_user": self.user,
                "db_password": self.password,
                "database": self.name,
                "no-database-list": not self.show,
                "db_maxconn": self.max_conn,
                "db-filter": self.filter,
            }
        )
        return res

    def compute_auto_maxconn(self, curr_env: api.Env) -> int:
        """
        Compute the current maxconn based on the number of worker
        Odoo recomendation is ~= Number of worker * 1.5.
        Args:
            curr_env: The current Env

        Returns:
            The number of worker * 1.5
        """
        nb_workers = _WorkersOdooConfigSection().init(curr_env).worker
        return nb_workers + int(nb_workers // 2)
