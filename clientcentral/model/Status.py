from typing import Optional


class Status:
    status_id: str
    email: str

    def __init__(self, status_id: str, name: Optional[str] = None):
        self.status_id = status_id
        self.name = name
