from hews.templates.back_senior_core import back_senior_core
from ...__constants__ import PROJECTS_DIR_NAME


class core(back_senior_core):
    def __init__(self, senior):
        super().__init__(__file__, senior, PROJECTS_DIR_NAME)
        from ..core import core as system_core_class
        self._sir_system_core: system_core_class = senior
        self._jun_project_cores = {}

    ####################################################################################################

    @property
    def sir_system_core(self):
        return self._sir_system_core

    ####################################################################################################

    def jun_project_core(self, name):
        if name not in self._jun_project_cores:
            from .project.core import core
            self._jun_project_cores[name] = core(self, name)
        return self._jun_project_cores[name]

    ####################################################################################################

    def console(self):
        pass
