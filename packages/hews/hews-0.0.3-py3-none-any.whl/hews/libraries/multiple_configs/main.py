from .single_configs_by_file import single_configs_by_file
from .single_configs_by_empty import single_configs_by_empty


class multiple_configs:
    def __init__(self, sys_file: str, def_file: str, sys_module: str = "configs", def_module: str = "configs"):
        self._system = single_configs_by_file(sys_file, sys_module)
        self._default = single_configs_by_file(def_file, def_module)
        self._user = single_configs_by_empty()

    @property
    def system(self) -> single_configs_by_file:
        return self._system

    @property
    def default(self) -> single_configs_by_file:
        return self._default

    @property
    def user(self) -> single_configs_by_empty:
        return self._user

    def get(self, key: str) -> str | None:
        result = self.user.get(key)
        if result is not None:
            return result
        result = self.default.get(key)
        if result is not None:
            return result
        result = self.system.get(key)
        if result is not None:
            return result
        return None
