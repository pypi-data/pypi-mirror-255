import os
import sys
from hews.templates.back_junior_core import back_junior_core
from hews.__constants__ import ROOT_DIR_NAME


class core(back_junior_core):
    def __init__(self):
        super().__init__(__file__, None, ROOT_DIR_NAME, os.path.dirname(os.path.abspath(sys.argv[0])))
        self._jun_projects_core = None

    ####################################################################################################

    @property
    def jun_projects_core(self):
        if self._jun_projects_core is None:
            from .projects.core import core
            self._jun_projects_core = core(self)
        return self._jun_projects_core

    def jun_project_core(self, name):
        return self.jun_projects_core.jun_project_core(name)

    ####################################################################################################

    def console(self):
        pass

    ####################################################################################################

    def service(self):
        pass
