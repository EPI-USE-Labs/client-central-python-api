#  "event_changes":[
#                {
#                   "id":427446,
#                   "_type":"TicketEventChange",
#                   "change_type":{
#                      "id":3,
#                      "name":"watcher",
#                      "_type":"TicketChangeType"
#                   },
#                   "to_value":"14015",
#                   "from_value":null,
#                   "name":"watchers"
#                }

from typing import List, Optional

from clientcentral.model.Change import Change
from clientcentral.model.TicketEvent import TicketEvent
from clientcentral.model.User import User


class ChangeEvent(TicketEvent):
    changes: List[Change]
    comment: Optional[str] = None

    def __init__(
        self,
        created_by_user: Optional[User],
        created_at: str,
        changes: List[Change],
        internal: bool,
        comment: Optional[str] = None,
    ):
        super().__init__(created_by_user, created_at, internal)
        self.changes = changes
        self.comment = comment
