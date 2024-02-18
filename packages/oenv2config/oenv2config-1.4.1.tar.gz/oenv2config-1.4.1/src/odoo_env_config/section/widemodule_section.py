from collections import OrderedDict

from typing_extensions import Self

from .. import api, utils


class ServerWideModuleConfigSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.server_wide_modules = []

    def init(self, curr_env: api.Env) -> Self:
        str_server_wide_modules = curr_env.get("SERVER_WIDE_MODULES")
        server_wide_modules = (
            str_server_wide_modules and list(OrderedDict().fromkeys(str_server_wide_modules.split(",")).keys()) or []
        )
        for suffix_key, value in curr_env.get_start_with("LOAD_"):
            if utils.is_number(value) or utils.is_bool(value):
                if utils.to_bool(value):
                    server_wide_modules.append(suffix_key.lower())
            else:
                server_wide_modules.append(value.lower())
        self.server_wide_modules = server_wide_modules
        return self

    def to_values(self) -> api.OdooCliFlag:
        return super().to_values().set("load", self.server_wide_modules)
