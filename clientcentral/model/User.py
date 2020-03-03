class User:
    user_id: str
    title: str
    job_title: str
    first_name: str
    last_name: str
    email: str

    def __init__(
        self,
        user_id: str,
        first_name: str,
        last_name: str,
        email: str,
        title: str = None,
        job_title: str = None,
    ):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

        self.title = title
        self.job_title = job_title

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
        )
        return user_obj

    name = property(get_name, set_name)
