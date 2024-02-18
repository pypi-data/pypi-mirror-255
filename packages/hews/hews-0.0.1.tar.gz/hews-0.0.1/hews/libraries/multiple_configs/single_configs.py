class single_configs:
    def __init__(self):
        self._cache = {}

    @property
    def all(self) -> dict:
        return self._cache

    def get(self, key: str) -> str:
        return self._cache.get(key)
