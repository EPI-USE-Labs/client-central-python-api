from typing import Optional


class Status:
    status_id: str
    name: str
    open: bool

    def __init__(self, status_id: str, open=True, name: Optional[str] = None):
        self.status_id = status_id
        self.name = name
        self.open = open

    @property
    def closed(self):
        return not self.open
