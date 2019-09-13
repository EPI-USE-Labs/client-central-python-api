#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

import ujson
import aiohttp
import asyncio

from clientcentral.Exceptions import HTTPError
from clientcentral.model.User import User

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class UsersManager:
    def __init__(
        self, base_url: str, token: str, production: bool, session=None, event_loop=None
    ) -> None:
        self._base_url = base_url
        self._token = token
        self.production = production
        self.session = session
        self._event_loop = event_loop
        self._net_calls = 0

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

    def get_user_by_id(self, user_id: int) -> User:
        url = self._base_url + "/api/v1/users/" + str(user_id) + ".json?" + self._token

        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        # Call URL
        future = asyncio.ensure_future(self._request("GET", url))
        response = self._event_loop.run_until_complete(future)

        if response["status_code"] != 200:
            raise HTTPError(response["json"])

        result_data = response["json"]["data"]

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
