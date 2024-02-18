from typing import Union

from typing_extensions import Self

from .. import api


class HttpOdooConfigSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.enable: bool = False
        self.interface: Union[str, None] = None
        self.port: int = 0
        self.longpolling_port: int = 0

    def init(self, curr_env: api.Env) -> Self:
        self.enable = curr_env.get_bool("HTTP_ENABLE", default=True)
        self.interface = curr_env.get("HTTP_INTERFACE")
        self.port = curr_env.get_int("HTTP_PORT")
        self.longpolling_port = curr_env.get_int("LONGPOLLING_PORT")
        return self

    def to_values(self) -> api.OdooCliFlag:
        res = super().to_values()
        if not self.enable:
            return res.set("no-http", True)

        res.set("http-interface", self.interface)
        res.set("http-port", self.port)
        res.set("longpolling-port", self.longpolling_port)
        return res
