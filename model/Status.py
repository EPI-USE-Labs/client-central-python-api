class Status:
    status_id = None
    email = None

    def __init__(self, status_id: str, name: str):
        self.status_id = status_id
        self.name = name
