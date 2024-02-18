from hews.templates.back_senior_core import back_senior_core
from .....__constants__ import APPLICATIONS_DIR_NAME


class core(back_senior_core):
    def __init__(self, senior):
        super().__init__(__file__, senior, APPLICATIONS_DIR_NAME)
        from ..core import core as project_core_class
        self._sir_project_core: project_core_class = senior
        from ...core import core as projects_core_class
        self._sir_projects_core: projects_core_class = self._sir_project_core.sir_projects_core
        from ....core import core as system_core_class
        self._sir_system_core: system_core_class = self._sir_project_core.sir_system_core
        self._jun_application_cores = {}

    ####################################################################################################

    @property
    def sir_project_core(self):
        return self._sir_project_core

    @property
    def sir_projects_core(self):
        return self._sir_projects_core

    @property
    def sir_system_core(self):
        return self._sir_system_core

    ####################################################################################################

    def jun_application_cores(self, name):
        if name not in self._jun_application_cores:
            from .application.core import core
            self._jun_application_cores[name] = core(self, name)
        return self._jun_application_cores[name]

    ####################################################################################################

    def console(self):
        pass

    ####################################################################################################

    def service(self):
        pass

