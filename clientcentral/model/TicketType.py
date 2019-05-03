from typing import Optional


class TicketType:
    type_id: int
    name: Optional[str]

    def __init__(self, type_id: int, name: Optional[str] = None):
        self.type_id = type_id
        self.name = name
