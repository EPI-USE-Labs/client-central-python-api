from typing import Optional

from clientcentral.model.TicketEvent import TicketEvent
from clientcentral.model.User import User

from bs4 import BeautifulSoup


class Comment(TicketEvent):
    def __init__(
        self,
        created_by_user: Optional[User],
        comment: str,
        created_at: str,
        internal: bool,
    ):
        super().__init__(created_by_user, created_at, internal)
        self.comment = comment

    def get_comment_text(self):
        soup = BeautifulSoup(str(self.comment), features="html.parser")
        return soup.get_text()
