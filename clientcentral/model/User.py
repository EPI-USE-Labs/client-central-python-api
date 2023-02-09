from typing import Optional


class User:
    def __init__(
        self,
        user_id: int,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        title: Optional[str] = None,
        job_title: Optional[str] = None,
        resource_owner_id: Optional[int] = None,
    ):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

        self.title = title
        self.job_title = job_title
        self.resource_owner_id = resource_owner_id

    def get_name(self):
        return self.first_name + " " + self.last_name

    def set_name(self, name):
        split_name = name.split(" ", 1)
        self.first_name = split_name[0]
        self.last_name = split_name[1]

    @classmethod
    def create_user_from_dict(cls, data: dict):
        user_obj = cls(
            data["id"],
            data["first_name"],
            data["last_name"],
            data["email"],
            data["title"],
            data["job_title"],
            data["number"],
        )
        return user_obj

    name = property(get_name, set_name)
