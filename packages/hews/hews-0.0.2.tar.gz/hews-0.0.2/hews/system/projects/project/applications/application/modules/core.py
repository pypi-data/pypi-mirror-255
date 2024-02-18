from hews.templates.back_senior_core import back_senior_core
from .......__constants__ import MODULES_DIR_NAME


class core(back_senior_core):
    def __init__(self, senior):
        super().__init__(__file__, senior, MODULES_DIR_NAME)
        from .module.core import core as module_core_class
        self._sir_module_core: module_core_class | None
        from ..core import core as application_core_class
        self._sir_application_core: application_core_class
        if isinstance(senior, module_core_class):
            self._sir_module_core = senior
            self._sir_application_core: application_core_class = self._sir_module_core.sir_application_core
        else:
            self._sir_module_core = None
            self._sir_application_core: application_core_class = senior
        from ...core import core as applications_core_class
        self._sir_applications_core: applications_core_class = self._sir_application_core.sir_applications_core
        from ....core import core as project_core_class
        self._sir_project_core: project_core_class = self._sir_application_core.sir_project_core
        from .....core import core as projects_core_class
        self._sir_projects_core: projects_core_class = self._sir_application_core.sir_projects_core
        from ......core import core as system_core_class
        self._sir_system_core: system_core_class = self._sir_application_core.sir_system_core
        self._jun_module_cores = {}

    ####################################################################################################

    @property
    def sir_module_core(self):
        return self._sir_module_core

    @property
    def sir_application_core(self):
        return self._sir_application_core

    @property
    def sir_applications_core(self):
        return self._sir_applications_core

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

    def jun_module_cores(self, name):
        if name not in self._jun_module_cores:
            from .module.core import core
            self._jun_module_cores[name] = core(self, name)
        return self._jun_module_cores[name]

    ####################################################################################################

    def console(self):
        pass

    ####################################################################################################

    def service(self):
        pass
