from hews.templates.back_junior_core import back_junior_core


class core(back_junior_core):
    def __init__(self, senior, name):
        super().__init__(__file__, senior, name)
        from ..core import core as projects_core_class
        self._sir_projects_core: projects_core_class = senior
        from ...core import core as system_core_class
        self._sir_system_core: system_core_class = self._sir_projects_core.sir_system_core
        self._jun_applications_core = None

    ####################################################################################################

    @property
    def sir_projects_core(self):
        return self._sir_projects_core

    @property
    def sir_system_core(self):
        return self._sir_system_core

    ####################################################################################################

    @property
    def jun_applications_core(self):
        if self._jun_applications_core is None:
            from .applications.core import core
            self._jun_applications_core = core(self)
        return self._jun_applications_core

    def jun_application_core(self, name):
        return self.jun_applications_core.jun_application_core(name)

    ####################################################################################################

    def console(self):
        pass

    ####################################################################################################

    def service(self):
        pass
