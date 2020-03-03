#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

import ujson
import aiohttp
import asyncio

from clientcentral.Exceptions import HTTPError
from clientcentral.model.Role import Role
from clientcentral.model.User import User

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class Roles:
    def __init__(
        self,
        base_url: str,
        token: str,
        production: bool,
        session: Optional[aiohttp.ClientSession] = None,
        event_loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._base_url = base_url
        self._token = token
        self.production = production
        self._net_calls = 0
        self.session = session
        self._event_loop = event_loop

    def _get_event_loop(self):
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    async def _request(self, http_verb, url, json=None, headers=None):
        """Submit the HTTP request with the running session or a new session."""
        self._net_calls += 1

        if not headers:
            headers = HEADERS

        if self.session and not self.session.closed:
            async with self.session.request(
                http_verb, url, headers=headers, json=json
            ) as resp:
                return {
                    "json": await resp.json(),
                    "headers": resp.headers,
                    "status_code": resp.status,
                }

        async with aiohttp.ClientSession(
            loop=self._event_loop, json_serialize=ujson.dumps
        ) as session:
            self.session = session
            async with self.session.request(
                http_verb, url, headers=headers, json=json
            ) as resp:
                return {
                    "json": await resp.json(),
                    "headers": resp.headers,
                    "status_code": resp.status,
                }

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

        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        # Call URL
        future = asyncio.ensure_future(self._request("GET", url))
        response = self._get_event_loop().run_until_complete(future)

        if response["status_code"] != 200:
            raise HTTPError("Failed to get all roles", response)
        result: List[Dict[str, str]] = response["json"]

        self._roles = list()

        for role in result:
            # Create new role object
            role_users: List[User] = []

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
