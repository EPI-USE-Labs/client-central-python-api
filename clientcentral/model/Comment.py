from clientcentral.model.TicketEvent import TicketEvent
from clientcentral.model.User import User


class Comment(TicketEvent):
    comment: str

    def __init__(self, created_by_user: User, comment: str, created_at: str):
        super().__init__(created_by_user, created_at)
        self.comment = comment
