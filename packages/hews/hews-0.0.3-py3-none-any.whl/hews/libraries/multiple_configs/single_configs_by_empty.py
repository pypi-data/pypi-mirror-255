from .single_configs import single_configs


class single_configs_by_empty(single_configs):
    def set(self, key: str, value):
        self._cache[key] = value
