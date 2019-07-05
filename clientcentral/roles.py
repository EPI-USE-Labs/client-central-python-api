#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional
from clientcentral.config import Config

import json
import requests

from clientcentral.Exceptions import HTTPError
from clientcentral.model.Role import Role


class Roles:

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(
        self, base_url: str, token: str, config: Config, production: bool
    ) -> None:
        self._base_url = base_url
        self._token = token
        self.config = config
        self.production = production

    @property
    def roles(self):
        if not hasattr(self, "_roles"):
            self.get_all_roles()
        return self._roles

    def get_all_users_in_role(self, role_name):
        for role in self.roles:
            if role.role_name == role_name:
                # Found role return user_ids
                return role.users

    def get_role_by_name(self, role_name: str) -> Role:
        for role in self.roles:
            if role.role_name == role_name:
                return role

    def get_all_roles(self):
        url = self._base_url + "/account/roles.json?" + self._token

        # Call URL
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        result = json.loads(response.text)

        self._roles = list()

        for role in result:
            # Create new role object
            role_users = []

            for user in role["users"]:
                role_users.append(user["id"])

            self._roles.append(
                Role(
                    role_id=role["id"],
                    role_name=role["name"],
                    account_id=role["account_id"],
                    default=role["default"],
                    users=role_users,
                )
            )

        return self._roles
