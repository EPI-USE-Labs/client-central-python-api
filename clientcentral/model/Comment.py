from typing import Optional

from clientcentral.model.TicketEvent import TicketEvent
from clientcentral.model.User import User

from bs4 import BeautifulSoup


class Comment(TicketEvent):
    comment: str

    def __init__(
        self,
        created_by_user: Optional[User],
        comment: str,
        created_at: str,
        visible_to_customer: bool,
    ):
        super().__init__(created_by_user, created_at, visible_to_customer)
        self.comment = comment

    def get_comment_text(self):
        soup = BeautifulSoup(str(self.comment), features="html.parser")
        return soup.get_text()
