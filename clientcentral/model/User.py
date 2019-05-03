class User:
    user_id: str
    name: str
    email: str

    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
