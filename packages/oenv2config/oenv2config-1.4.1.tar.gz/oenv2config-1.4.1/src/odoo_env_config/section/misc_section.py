import os
from typing import List

from typing_extensions import Self

from .. import api


class MiscSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.unaccent = False
        self.without_demo: List[str] = []
        self.stop_after_init = False
        self.admin_password = False
        self.save_config_file = False
        self.data_dir = None

    def init(self, curr_env: api.Env) -> Self:
        self.unaccent = curr_env.get_bool("UNACCENT", default=False)
        self.without_demo = curr_env.get_list("WITHOUT_DEMO")
        if curr_env.is_boolean("WITHOUT_DEMO") and curr_env.get_bool("WITHOUT_DEMO"):
            # When WITHOUT_DEMO=True, then we set to `all`
            self.without_demo = ["all"]
        self.stop_after_init = curr_env.get_bool("STOP_AFTER_INIT")
        self.save_config_file = curr_env.get_bool("SAVE_CONFIG_FILE")
        self.data_dir = curr_env.get("DATA_DIR")
        if curr_env.get("ODOO_PATH"):
            self.data_dir = os.path.join(curr_env.get("ODOO_PATH"), self.data_dir)

        self.admin_password = curr_env.gets("ADMIN_PASSWORD", "ADMIN_PASSWD", "ODOO_ADMIN_PASSWORD")
        return self

    def to_values(self) -> api.OdooCliFlag:
        flags = super().to_values()
        flags.set("unaccent", self.unaccent)
        flags.set("without-demo", ",".join(self.without_demo))
        flags.set("save", self.save_config_file)
        flags.set("stop-after-init", self.stop_after_init)
        flags.set("data-dir", self.data_dir)
        return flags
