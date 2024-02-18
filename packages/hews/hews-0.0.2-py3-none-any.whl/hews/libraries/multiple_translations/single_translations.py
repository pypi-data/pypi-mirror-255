class single_translations:
    def __init__(self, path: str, module: str = "translations"):
        super().__init__()
        self._path = path
        self._module = module
        self.load()
        self._cache = {}

    @property
    def path(self):
        return self._path

    def load(self) -> bool:
        import heuf
        r = heuf.file.import_dict.from_py_file(self.path, self._module)
        if r is None:
            return False
        self._cache = r
        return True

    @property
    def all(self) -> dict:
        return self._cache

    def get(self, key: str) -> str:
        r = self.read(key)
        if r is not None:
            return r
        return key

    def read(self, key: str) -> str | None:
        return self._cache.get(key)
