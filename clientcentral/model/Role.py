from typing import List


class Role:
    role_id: int
    role_name: str
    account_id: int
    default: bool
    users: List[any]

    def __init__(
        self, role_id: int, role_name: str, account_id: int, users: List, default=False
    ):
        self.role_id = role_id
        self.role_name = role_name
        self.account_id = account_id
        self.users = users
        self.default = default
