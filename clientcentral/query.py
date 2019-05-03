# query().filter_by(Comparison("created_by_user.name", "=", "name"))
import json
from datetime import datetime

import requests

from typing import List

from clientcentral.Exceptions import HTTPError
from clientcentral.model.Status import Status
from clientcentral.model.TicketType import TicketType
from clientcentral.model.User import User
from clientcentral.ticket import Ticket
from clientcentral.config import Config

class QueryTickets:
    _query: str

    base_url: str
    token: str

    config: Config
    production: bool = False

    def __init__(self, base_url: str, token: str, config: Config, production: bool) -> None:
        self._query = ""
        self.base_url = base_url
        self.token = token
        self.config = config
        self.production = production

    def filter_by(self, arg: str) -> "QueryTickets":
        self._query = "&filter=" + str(arg)
        # print(self._query)
        return self

    def all(self) -> List[Ticket]:
        url = self.base_url + "/api/v1/tickets.json?" + self.token
        payload = self._query + "&select=type.*,events.comment,events.created_by_user.email,events.created_by_user.name,events.created_at,created_by_user.email,created_by_user.name,subject,description,priority.name,user_watchers.email,user_watchers.name,status.name,*"
        response = requests.get(url + payload)
        # print(response.text)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        result = json.loads(response.text)
        tickets = []

        for page in range(1, (result["total_pages"] + 1)):
            for ticket_in_data in result["data"]:
                ticket = Ticket(
                    base_url=self.base_url,
                    token=self.token,
                    ticket_id=str(ticket_in_data["id"]),
                    config=self.config,
                    production=self.production,
                    workspace_id=ticket_in_data["workspace"]["id"],
                    project_id=ticket_in_data["project"]["id"],
                    status=Status(
                        status_id=ticket_in_data["status"]["id"],
                        name=ticket_in_data["status"]["id"]),
                    created_at=datetime.strptime(ticket_in_data["created_at"],
                                                 "%Y-%m-%dT%H:%M:%S.%f%z"),
                    updated_at=datetime.strptime(ticket_in_data["updated_at"],
                                                 "%Y-%m-%dT%H:%M:%S.%f%z"),
                    description=ticket_in_data["description"],
                    subject=ticket_in_data["subject"],
                    owner=User(
                        user_id=ticket_in_data["created_by_user"]["id"],
                        name=ticket_in_data["created_by_user"]["name"],
                        email=ticket_in_data["created_by_user"]["email"]),
                    ticket_type=TicketType(
                        type_id=ticket_in_data["type"]["id"],
                        name=ticket_in_data["type"]["name"]),
                    user_watchers=[
                        User(
                            user_id=user["id"],
                            name=user["name"],
                            email=user["email"])
                        for user in ticket_in_data["user_watchers"]
                    ],
                    priority=ticket_in_data["priority"]["id"])
                if ticket_in_data["assignee"]:
                    ticket.assignee = ticket_in_data["assignee"]["id"]
                tickets.append(ticket)

            # print("PAGE: " + str(page + 1))
            response = requests.get(url + "&page=" + str(page + 1) + payload)
            if response.status_code != 200:
                raise HTTPError(response.text)
            response.raise_for_status()
            result = json.loads(response.text)

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
    return str(left) + "%20" + str(operator) + "%20" + str(right)
