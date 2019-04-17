from datetime import datetime

from model.User import User


class Comment:
    creator: User = None
    description: str = None
    created_at: datetime = None

    def __init__(self, creator: User, description: str, created_at):
        self.creator = creator
        self.description = description
        self.created_at = datetime.strptime(created_at,
                                            "%Y-%m-%dT%H:%M:%S.%f%z")
