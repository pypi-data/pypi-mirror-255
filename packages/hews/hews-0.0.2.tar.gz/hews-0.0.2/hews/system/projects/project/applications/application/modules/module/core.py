from hews.templates.back_junior_core import back_junior_core


class core(back_junior_core):
    def __init__(self, senior, name):
        super().__init__(__file__, senior, name)
        from ..core import core as modules_core_class
        self._sir_modules_core: modules_core_class = senior
        from ...core import core as application_core_class
        self._sir_application_core: application_core_class = self._sir_modules_core.sir_application_core
        from ....core import core as applications_core_class
        self._sir_applications_core: applications_core_class = self._sir_modules_core.sir_applications_core
        from .....core import core as project_core_class
        self._sir_project_core: project_core_class = self._sir_modules_core.sir_project_core
        from ......core import core as projects_core_class
        self._sir_projects_core: projects_core_class = self._sir_modules_core.sir_projects_core
        from .......core import core as system_core_class
        self._sir_system_core: system_core_class = self._sir_modules_core.sir_system_core
        self._jun_modules_core = None

    ####################################################################################################

    @property
    def sir_modules_core(self):
        return self._sir_modules_core

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

    @property
    def jun_modules_core(self):
        if self._jun_modules_core is None:
            from ...modules.core import core
            self._jun_modules_core = core(self)
        return self._jun_modules_core

    def jun_module_core(self, name):
        return self.jun_modules_core.jun_module_core(name)

    ####################################################################################################

    def console(self):
        pass

    ####################################################################################################

    def service(self):
        pass


