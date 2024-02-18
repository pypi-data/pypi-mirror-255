from .single_configs import single_configs


class single_configs_by_file(single_configs):
    def __init__(self, file: str, name: str = "settings"):
        super().__init__()
        self._file = file
        self._name = name
        self.load()

    @property
    def file(self):
        return self._file

    def load(self) -> bool:
        import heuf
        r = heuf.file.import_dict.from_py_file(self._file, self._name)
        if r is None:
            return False
        self._cache = r
        return True
