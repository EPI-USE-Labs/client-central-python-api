#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

import ujson
import aiohttp
import asyncio

import clientcentral.query as query
from clientcentral.Exceptions import HTTPError
from clientcentral.model.User import User

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class UsersClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        production: bool,
        session=None,
        event_loop=None,
        run_async=False,
    ) -> None:
        self._base_url = base_url
        self._token = token
        self.production = production
        self.session = session
        self._event_loop = event_loop
        self._net_calls = 0
        self._run_async = run_async

    def _get_event_loop(self):
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_running_loop()
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
                    "method": resp.method,
                    "url": resp.url,
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
                    "method": resp.method,
                    "url": resp.url,
                }

    async def _async_get_user_by_id(self, url: str, user_id: int) -> User:
        # Call URL
        response = await self._request("GET", url)

        if response["status_code"] != 200:
            raise HTTPError(f"Failed to get user by id: {user_id}", response)

        result_data = response["json"]["data"]
        return User.create_user_from_dict(result_data)

    def get_user_by_id(self, user_id: int) -> User:
        url = self._base_url + "/api/v1/users/" + str(user_id) + ".json?" + self._token

        if self._run_async:
            return self._async_get_user_by_id(url, user_id)

        # Call URL
        future = self._event_loop.create_task(self._request("GET", url))
        response = self._event_loop.run_until_complete(future)

        if response["status_code"] != 200:
            raise HTTPError(f"Failed to get user by id: {user_id}", response)

        result_data = response["json"]["data"]
        return User.create_user_from_dict(result_data)

    async def _async_get_user_by_email(self, url: str, user_email: str) -> User:
        # Call URL
        response = await self._request("GET", url)

        if response["status_code"] != 200:
            raise HTTPError(f"Failed to get user by email: {user_email}", response)

        result_data = response["json"]["data"][0]
        return User.create_user_from_dict(result_data)

    def get_user_by_email(self, user_email: str) -> User:
        url = (
            self._base_url
            + "/api/v1/users.json?"
            + self._token
            + "&filter="
            + query.comparison("email", "=", "'" + user_email + "'")
        )

        if self._run_async:
            return self._async_get_user_by_email(url, user_email)

        # Call URL
        future = self._event_loop.create_task(self._request("GET", url))
        response = self._event_loop.run_until_complete(future)

        if response["status_code"] != 200:
            raise HTTPError(f"Failed to get user by email: {user_email}", response)

        result_data = response["json"]["data"][0]
        return User.create_user_from_dict(result_data)

    def get_all_users(self):
        raise Exception("Unimplemented")

    def lock_user_by_email(self, user_email: str):
        # /api/v1/users/:id/lock
        user = self.get_user_by_email(user_email)
        url = (
            self._base_url
            + "/api/v1/users/"
            + str(user.number)
            + "/lock?"
            + self._token
        )

        # Call URL
        future = self._event_loop.create_task(self._request("PUT", url))
        response = self._event_loop.run_until_complete(future)

        if response["status_code"] != 200:
            raise HTTPError(f"Failed to lock user by email: {user_email}", response)

    def unlock_user_by_email(self, user_email: str):
        # /api/v1/users/:id/unlock
        user = self.get_user_by_email(user_email)
        url = (
            self._base_url
            + "/api/v1/users/"
            + str(user.number)
            + "/unlock?"
            + self._token
        )

        # Call URL
        future = self._event_loop.create_task(self._request("PUT", url))
        response = self._event_loop.run_until_complete(future)

        if response["status_code"] != 200:
            raise HTTPError(f"Failed to unlock user by email: {user_email}", response)


# user_id: str,
# first_name: str,
# last_name: str,
# email: str,
# title: str = None,
# job_title: str = None,
