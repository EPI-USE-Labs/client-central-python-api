from datetime import datetime
from typing import Optional

from clientcentral.model.User import User
from clientcentral.Exceptions import DateFormatInvalid


class TicketEvent:
    def __init__(
        self,
        created_by_user: Optional[User],
        created_at: str,
        internal: bool,
    ):
        self.created_by_user = created_by_user
        # Created at
        try:
            self.created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            pass

        try:
            self.created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            pass

        if self.created_at == None:
            raise DateFormatInvalid("Failed to convert datetime: " + created_at)
        self.internal = internal
