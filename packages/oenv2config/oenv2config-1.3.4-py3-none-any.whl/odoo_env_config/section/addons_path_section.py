from typing import List

from addons_installer import addons_installer
from typing_extensions import Self

from .. import api


class AddonsPathConfigSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.registry = addons_installer.AddonsFinder()
        self.addons_path: List[str] = []

    def init(self, curr_env: api.Env) -> Self:
        result = self.registry.parse_env(env_vars=curr_env)
        self.addons_path = [r.addons_path for r in result]
        return self

    def to_values(self) -> api.OdooCliFlag:
        res = super().to_values()
        res.set("addons-path", self.addons_path)
        return res
