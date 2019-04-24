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

from typing import List

from model.Change import Change
from model.TicketEvent import TicketEvent
from model.User import User


class ChangeEvent(TicketEvent):
    changes: List[Change] = None
    comment: str = None

    def __init__(self,
                 created_by_user: User,
                 created_at: str,
                 changes: List[Change],
                 comment=None):
        super().__init__(created_by_user, created_at)
        self.changes = changes
        self.comment = comment
