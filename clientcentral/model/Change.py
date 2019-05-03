class Change:
    name: str
    to_value: str
    from_value: str

    def __init__(self, name: str, to_value: str, from_value: str):
        self.name = name
        self.to_value = to_value
        self.from_value = from_value
