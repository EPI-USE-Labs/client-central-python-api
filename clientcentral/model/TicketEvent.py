from datetime import datetime

from clientcentral.model.User import User


class TicketEvent:
    created_by_user: User = None
    created_at: datetime = None

    def __init__(self, created_by_user: User, created_at: str):
        self.created_by_user = created_by_user
        self.created_at = datetime.strptime(created_at,
                                            "%Y-%m-%dT%H:%M:%S.%f%z")
