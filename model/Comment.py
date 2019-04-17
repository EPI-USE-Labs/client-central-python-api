from datetime import datetime

from model.User import User


class Comment:
    created_by_user: User = None
    description: str = None
    created_at: datetime = None

    def __init__(self, created_by_user: User, description: str, created_at):
        self.created_by_user = created_by_user
        self.description = description
        self.created_at = datetime.strptime(created_at,
                                            "%Y-%m-%dT%H:%M:%S.%f%z")
