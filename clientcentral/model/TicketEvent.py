from datetime import datetime
from typing import Optional

from clientcentral.model.User import User


class TicketEvent:
    created_by_user: Optional[User] = None
    created_at: datetime
    visible_to_customer: bool

    def __init__(
        self,
        created_by_user: Optional[User],
        created_at: str,
        visible_to_customer: bool,
    ):
        self.created_by_user = created_by_user
        self.created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
        self.visible_to_customer = visible_to_customer
