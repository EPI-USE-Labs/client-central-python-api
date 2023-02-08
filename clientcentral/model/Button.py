class Button:
    def __init__(
        self,
        button_id: str,
        enabled: bool,
        name: str,
        agent_only: bool,
        require_comment: bool,
        colour: str,
    ) -> None:
        self.button_id = button_id
        self.enabled = enabled
        self.name = name
        self.agent_only = agent_only
        self.require_comment = require_comment
        self.colour = colour
