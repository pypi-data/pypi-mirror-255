import os


class back_node_core:
    def __init__(self, x_file, senior, name, path=None):
        self._x_file = x_file
        self._x_path = os.path.dirname(os.path.abspath(x_file))
        self._senior = senior
        self._name = name
        self._tree = None
        self._path = path
        self._namespace = None
        pass

    @property
    def x_path(self):
        return self._x_path

    @property
    def senior(self):
        return self._senior

    @property
    def name(self):
        return self._name

    @property
    def tree(self) -> list:
        if self._tree is None:
            if self.senior is None:
                self._tree = [self.name]
            else:
                self._tree = [*self.senior.tree, self.name]
        return self._tree

    @property
    def path(self) -> str:
        if self._path is None:
            if self.senior is not None:
                self._path = os.path.join(self.senior.path, self.name)
        return self._path

    @property
    def namespace(self) -> str:
        if self._namespace is None:
            if self.senior is None:
                self._namespace = self.name
            else:
                self._namespace = ".".join([self.senior.namespace, self.name])
        return self._namespace
