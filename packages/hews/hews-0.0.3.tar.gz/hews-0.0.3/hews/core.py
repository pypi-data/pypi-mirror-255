class core:
    def __init__(self):
        self._system = None
        self._clients = {}
        pass

    @property
    def system(self):
        if self._system is None:
            from system.core import core
            self._system = core()
        return self._system

    def client(self, session_id):
        if session_id not in self._clients:
            from client.core import core
            self._clients[session_id] = core(session_id)

    ####################################################################################################

    def console(self):
        pass

    ####################################################################################################

    def service(self):
        return "Hello World"

x = core()
