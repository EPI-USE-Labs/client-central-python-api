class User:
    user_id: str
    title: str
    job_title: str
    first_name: str
    last_name: str
    email: str

    def __init__(self,
                 user_id: str,
                 first_name: str,
                 last_name: str,
                 email: str,
                 title: str = None,
                 job_title: str = None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

        self.title = title
        self.job_title = job_title
