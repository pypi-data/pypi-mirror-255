class core:
    def __init__(self, session_id):
        self._id = session_id

    @property
    def id(self):
        return self._id
