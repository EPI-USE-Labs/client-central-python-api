#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List

import ujson
import aiohttp
import asyncio

from clientcentral.Exceptions import HTTPError
from clientcentral.model.Status import Status
from clientcentral.model.TicketType import TicketType
from clientcentral.model.User import User
from clientcentral.ticket import Ticket

from clientcentral.Exceptions import DateFormatInvalid

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class QueryTickets:
    def __init__(
        self, base_url: str, token: str, production: bool, session=None, event_loop=None
    ) -> None:
        self._query = ""
        self.base_url = base_url
        self.token = token
        self.production = production
        self._event_loop = event_loop
        self.session = session
        self._net_calls = 0

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

    def filter_by(self, arg: str) -> "QueryTickets":
        self._query = "&filter=" + str(arg)
        # print(self._query)
        return self

    def all(self) -> List[Ticket]:
        url = self.base_url + "/api/v1/tickets.json?" + self.token
        payload = self._query

        selection = [
            "subject",
            "description",
            "priority.name",
            "status.name",
            "status.closed",
            "customer_user.*",
            "type.*",
            "assignee.*",
            "created_by_user.email",
            "created_by_user.title",
            "created_by_user.job_title",
            "created_by_user.first_name",
            "created_by_user.last_name",
            "user_watchers.email",
            "user_watchers.first_name",
            "user_watchers.last_name",
            "user_watchers.title",
            "user_watchers.job_title",
        ]

        payload += "&select="
        payload += ",".join(selection)
        payload += ",*"

        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._request("GET", url + payload))
        response = self._event_loop.run_until_complete(future)

        # response = requests.get(url + payload)

        if response["status_code"] != 200:
            raise HTTPError("Failed to query all tickets", response)
        result = response["json"]
        tickets = []

        for page in range(1, (result["total_pages"] + 1)):
            for ticket_in_data in result["data"]:
                creator = None
                if ticket_in_data["created_by_user"]:
                    creator = User(
                        user_id=ticket_in_data["created_by_user"]["id"],
                        first_name=ticket_in_data["created_by_user"]["first_name"],
                        last_name=ticket_in_data["created_by_user"]["last_name"],
                        job_title=ticket_in_data["created_by_user"]["job_title"],
                        email=ticket_in_data["created_by_user"]["email"],
                    )
                    if ticket_in_data["created_by_user"]["title"]:
                        creator.title = ticket_in_data["created_by_user"]["title"][
                            "name"
                        ]

                owner = None
                if ticket_in_data["customer_user"]:
                    owner = User(
                        user_id=ticket_in_data["customer_user"]["id"],
                        first_name=ticket_in_data["customer_user"]["first_name"],
                        last_name=ticket_in_data["customer_user"]["last_name"],
                        job_title=ticket_in_data["customer_user"]["job_title"],
                        email=ticket_in_data["customer_user"]["email"],
                    )
                    if ticket_in_data["customer_user"]["title"]:
                        owner.title = ticket_in_data["customer_user"]["title"]["name"]

                assignee = None
                if ticket_in_data["assignee"]:
                    assignee = (
                        ticket_in_data["assignee"]["_type"]
                        + ":"
                        + str(ticket_in_data["assignee"]["id"])
                    )

                account_vp = None
                if ticket_in_data["account"] and (
                    ticket_in_data["account"] is not None
                ):
                    account_vp = ticket_in_data["account"]["id"]

                customer_user_vp = None
                if ticket_in_data["customer_user"] and (
                    ticket_in_data["customer_user"] is not None
                ):
                    customer_user_vp = ticket_in_data["customer_user"]["id"]

                # Created at
                try:
                    ticket_created_at = datetime.strptime(
                        ticket_in_data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
                    )
                except ValueError:
                    pass

                try:
                    ticket_created_at = datetime.strptime(
                        ticket_in_data["created_at"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                except ValueError:
                    pass

                if ticket_created_at == None:
                    raise DateFormatInvalid(
                        "Failed to convert datetime: "
                        + str(ticket_in_data["created_at"])
                    )

                # Updated at
                try:
                    ticket_updated_at = datetime.strptime(
                        ticket_in_data["updated_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
                    )
                except ValueError:
                    pass

                try:
                    ticket_updated_at = datetime.strptime(
                        ticket_in_data["updated_at"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                except ValueError:
                    pass

                if ticket_updated_at == None:
                    raise DateFormatInvalid(
                        "Failed to convert datetime: "
                        + str(ticket_in_data["updated_at"])
                    )

                ticket = Ticket(
                    base_url=self.base_url,
                    token=self.token,
                    ticket_id=str(ticket_in_data["id"]),
                    production=self.production,
                    account_vp=account_vp,
                    customer_user_vp=customer_user_vp,
                    workspace_id=ticket_in_data["workspace"]["id"],
                    project_id=ticket_in_data["project"]["id"],
                    status=Status(
                        status_id=ticket_in_data["status"]["id"],
                        name=ticket_in_data["status"]["name"],
                        open=not ticket_in_data["status"]["closed"],
                    ),
                    created_at=ticket_created_at,
                    updated_at=ticket_updated_at,
                    description=ticket_in_data["description"],
                    subject=ticket_in_data["subject"],
                    owner=owner,
                    creator=creator,
                    assignee=assignee,
                    internal=ticket_in_data["internal"],
                    ticket_type=TicketType(
                        type_id=ticket_in_data["type"]["id"],
                        name=ticket_in_data["type"]["name"],
                    ),
                    user_watchers=[
                        User(
                            user_id=user["id"],
                            first_name=user["first_name"],
                            last_name=user["first_name"],
                            email=user["email"],
                        )
                        for user in ticket_in_data["user_watchers"]
                    ],
                    priority=ticket_in_data["priority"]["id"],
                    session=self.session,
                )
                # if ticket_in_data["assignee"]:
                #     ticket.assignee = ticket_in_data["assignee"]["id"]
                tickets.append(ticket)

            # print("PAGE: " + str(page + 1))

            future = self._event_loop.create_task(
                self._request("GET", url + "&page=" + str(page + 1) + payload)
            )
            response = self._event_loop.run_until_complete(future)

            # response = requests.get(url + "&page=" + str(page + 1) + payload)
            if response["status_code"] != 200:
                raise HTTPError("Failed to query all tickets", response)
            result = response["json"]
        return tickets


def and_(*argv: str) -> str:
    result = "("
    for i, arg in enumerate(argv):
        if i < len(argv) - 1:
            result += str(arg) + "%20AND%20"
        else:
            result += str(arg)
    result += ")"
    return result


def not_(arg: str) -> str:
    return "NOT%20" + str(arg)


def or_(*argv: str) -> str:
    result = "("
    for i, arg in enumerate(argv):
        if i < len(argv) - 1:
            result += str(arg) + "%20OR%20"
        else:
            result += str(arg)

    result += ")"
    return result


def statement(left: str) -> str:
    return str(left)


def comparison(left: str, operator: str, right: str) -> str:
    valid_operators = [
        "=",
        ">",
        "<",
        ">=",
        "<=",
        "<>",
        "CONTAINS",
        "NOT CONTAINS",
        "IN",
        "OR",
        "NOT",
    ]
    if operator not in valid_operators:
        raise Exception(
            "Invalid operator. Valid operators include: " + str(valid_operators)
        )
    return str(left) + "%20" + str(operator) + "%20" + str(right)
