from typing import Optional


class Attachment(object):
    def __init__(
        self,
        id: str,
        event: dict,
        original_filename: str,
        created_at: str,
        updated_at: str,
        inline: bool,
        content_type: str,
        link: str,
        path: Optional[str] = None,
    ) -> None:
        self.id = id
        self.event = event
        self.original_filename = original_filename
        self.created_at = created_at
        self.updated_at = updated_at
        self.inline = inline
        self.content_type = content_type
        self.link = link
