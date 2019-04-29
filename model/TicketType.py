class TicketType:
    type_id = None
    name = None

    def __init__(self, type_id: int, name: str):
        self.type_id = type_id
        self.name = name
