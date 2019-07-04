#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional
from clientcentral.config import Config

import json
import requests

from clientcentral.Exceptions import HTTPError
from clientcentral.model.User import User


class UsersManager:

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(
        self, base_url: str, token: str, config: Config, production: bool
    ) -> None:
        self._base_url = base_url
        self._token = token
        self.config = config
        self.production = production

    def get_user_by_id(self, user_id: int) -> User:
        url = self._base_url + "/api/v1/users/" + str(user_id) + ".json?" + self._token
        # Call URL
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        result = json.loads(response.text)

        result_data = result["data"]

        user_obj = User(
            result_data["id"],
            result_data["first_name"],
            result_data["last_name"],
            result_data["email"],
            result_data["title"],
            result_data["job_title"],
        )
        return user_obj

    def get_all_users(self):
        # TODO
        pass


# user_id: str,
# first_name: str,
# last_name: str,
# email: str,
# title: str = None,
# job_title: str = None,
