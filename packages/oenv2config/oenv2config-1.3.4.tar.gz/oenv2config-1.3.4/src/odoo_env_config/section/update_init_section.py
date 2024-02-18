from typing_extensions import Self

from .. import api


class UpdateInstallSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.update = []
        self.install = []

    def init(self, curr_env: api.Env) -> Self:
        self.update = curr_env.get_list("UPDATE")
        self.install = curr_env.get_list("INSTALL")
        return self

    def to_values(self) -> api.OdooCliFlag:
        flags = super().to_values()
        flags.set("update", self.update and ",".join(self.update))
        flags.set("init", self.install and ",".join(self.install))
        return flags
