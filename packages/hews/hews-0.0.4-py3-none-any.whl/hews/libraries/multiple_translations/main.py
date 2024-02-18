import os.path

from .single_translations import single_translations


class multiple_translations:
    def __init__(self, path: str, sys_language: str, def_language, usr_language: str,
                 sys_module: str = 'translations', def_module: str = 'translations', usr_module: str = 'translations'):
        self._path = path
        self._sys_langauge = sys_language
        self._def_langauge = def_language
        self._usr_langauge = usr_language
        self._packages = {}
        self._sys_module = sys_module
        self._def_module = def_module
        self._usr_module = usr_module

    @property
    def path(self) -> str:
        return self._path

    @property
    def system_language(self) -> str:
        return self._sys_langauge

    @property
    def default_langauge(self) -> str:
        return self._def_langauge

    @property
    def user_language(self) -> str:
        return self._usr_langauge

    def package_(self, langauge: str, module: str = "translations") -> single_translations:
        if langauge not in self._packages:
            self._packages[langauge] = single_translations(os.path.join(self.path, langauge + ".py"), module)
        return self._packages[langauge]

    @property
    def package_system(self) -> single_translations:
        return self.package_(self.system_language, self._sys_module)

    @property
    def package_default(self) -> single_translations:
        return self.package_(self.default_langauge, self._def_module)

    @property
    def package_user(self) -> single_translations:
        return self.package_(self.user_language, self._usr_module)

    def get(self, key: str) -> str:
        result = self.package_user.read(key)
        if result is not None:
            return result
        result = self.package_default.read(key)
        if result is not None:
            return result
        result = self.package_system.read(key)
        if result is not None:
            return result
        return key
