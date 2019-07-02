#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

import requests

from clientcentral.config import Config
from clientcentral.Exceptions import (
    ButtonNotAvailable,
    ButtonRequiresComment,
    HTTPError,
)
from clientcentral.model.Button import Button
from clientcentral.model.Change import Change
from clientcentral.model.ChangeEvent import ChangeEvent
from clientcentral.model.Comment import Comment
from clientcentral.model.Status import Status
from clientcentral.model.TicketEvent import TicketEvent
from clientcentral.model.TicketType import TicketType
from clientcentral.model.User import User


class Ticket:
    _production: bool = False

    _base_url: str
    _token: str

    subject: Optional[str]
    priority: Optional[int]
    ticket_id: str

    creator: Optional[User]
    owner: Optional[User]

    description: Optional[str]

    type: Optional[TicketType]

    visible_to_customer: bool

    workspace_id: int
    project_id: int

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    user_watchers: List[User]
    # email_watchers = None

    # Custom
    custom_fields_attributes: List[Dict[str, int]]

    # related_tickets: Optional[List[int]]

    # custom_fields: List[Dict[str, Any]]

    # available_buttons: List[Button]

    # comments: List[Comment] = None
    # events: List[TicketEvent] = None
    # change_events: List[ChangeEvent] = None

    status: Optional[Status]
    assignee = None

    config: Config
    button_ids = None

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(
        self,
        base_url: str,
        token: str,
        config: Config,
        ticket_id: str,
        production: bool,
        workspace_id: int,
        project_id: int,
        custom_fields_attributes: List[Dict[str, int]] = [],
        ticket_type: Optional[TicketType] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        status: Optional[Status] = None,
        description: Optional[str] = None,
        subject: Optional[str] = None,
        owner: Optional[User] = None,
        creator: Optional[User] = None,
        user_watchers: List[User] = [],
        priority: Optional[int] = None,
        assignee: Optional[str] = None,
        related_tickets: Optional[List[int]] = None,
        visible_to_customer: bool = True
    ) -> None:

        self.description = description
        self.subject = subject

        self.created_at = created_at
        self.updated_at = updated_at

        # self.events = []
        # self.change_events = []
        # self.comments = []
        self.user_watchers = user_watchers
        self.custom_fields_attributes = custom_fields_attributes

        self._related_tickets = related_tickets

        self.creator = creator
        self.owner = owner

        self.assignee = assignee

        self.visible_to_customer = visible_to_customer

        self._production = production
        self._base_url = base_url
        self._token = token
        self.ticket_id = ticket_id

        self.status = status

        self.type = ticket_type

        self.workspace_id = workspace_id
        self.project_id = project_id

        self.config = config

        self.priority = priority

        if not self.priority:
            self.priority = self.config.get()["ticket-priority"]["very-low"]

        self.button_ids = self.config.get()["button-ids"]

        if ticket_id and not self.created_at and not self.updated_at:
            self._update()

    def refresh(self) -> None:
        self._update()

    def _update_buttons(self):
        url = (
            self._base_url
            + "/api/v1/tickets/"
            + self.ticket_id
            + "/available_buttons.json?"
            + self._token
        )
        response = requests.get(url, headers=self.headers)
        # print(response.text)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()

        result = json.loads(response.text)

        self._available_buttons = list()

        for button in result["data"]:
            self._available_buttons.append(
                Button(
                    button_id=button["id"],
                    enabled=button["enabled"],
                    name=button["name"],
                    agent_only=button["agent_only"],
                    require_comment=button["require_comment"],
                    colour=button["colour"],
                )
            )
        return self._available_buttons

    # Call the button URL to get the current buttons.
    @property
    def available_buttons(self):
        if not hasattr(self, "_available_buttons"):
            self._update_buttons()

        return self._available_buttons

    def _update(self) -> None:
        # print("UPDATED!!!")

        result: Dict[str, Any] = self.get()

        self.description = str(result["data"]["description"]).strip()
        self.subject = str(result["data"]["subject"]).strip()

        new_status = Status(
            status_id=result["data"]["status"]["id"],
            name=result["data"]["status"]["name"],
        )

        if self.status != new_status:
            # Update buttons
            self._update_buttons()

        self.status = new_status

        self.priority = result["data"]["priority"]["id"]

        self.creator = User(
            user_id=result["data"]["created_by_user"]["id"],
            first_name=result["data"]["created_by_user"]["first_name"],
            last_name=result["data"]["created_by_user"]["last_name"],
            job_title=result["data"]["created_by_user"]["job_title"],
            email=result["data"]["created_by_user"]["email"],
        )
        if result["data"]["created_by_user"]["title"]:
            self.creator.title = result["data"]["created_by_user"]["title"]["name"]

        self.owner = User(
            user_id=result["data"]["customer_user"]["id"],
            first_name=result["data"]["customer_user"]["first_name"],
            last_name=result["data"]["customer_user"]["last_name"],
            job_title=result["data"]["customer_user"]["job_title"],
            email=result["data"]["customer_user"]["email"],
        )
        if result["data"]["customer_user"]["title"]:
            self.owner.title = result["data"]["customer_user"]["title"]["name"]

        self.created_at = datetime.strptime(
            result["data"]["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        self.updated_at = datetime.strptime(
            result["data"]["updated_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )

        self.project_id = result["data"]["project"]["id"]
        self.workspace_id = result["data"]["workspace"]["id"]

        self.visible_to_customer = result["data"]["visible_to_customer"]

        self.type = TicketType(
            type_id=result["data"]["type"]["id"], name=result["data"]["type"]["name"]
        )

        if result["data"]["assignee"]:
            self.assignee = (
                result["data"]["assignee"]["_type"]
                + ":"
                + str(result["data"]["assignee"]["id"])
            )

        self._related_tickets: List[int] = list()
        try:
            result["data"]["related_tickets"]
            # self.related_tickets = []
            for related_ticket in result["data"]["related_tickets"]:
                self._related_tickets.append(related_ticket["id"])
        except KeyError:
            pass

        self._custom_fields: dict = {}
        reserved_fields = [
            "description",
            "subject",
            "status",
            "created_by_user",
            "customer_user",
            "created_at",
            "updated_at",
            "project",
            "workspace",
            "type",
            "user_watchers",
            "events",
            "email_watcher_emails",
            "visible_to_customer",
            "priority",
            "last_event",
            "account",
            "assignee",
            "assignee_roles",
            "id",
            "related_tickets",
        ]

        for field_name in result["data"]:
            if field_name not in reserved_fields:
                self._custom_fields[field_name] = result["data"][field_name]

        self.user_watchers = []

        if result["data"]["user_watchers"]:
            for user in result["data"]["user_watchers"]:
                user_watcher = User(
                    user_id=user["id"],
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    job_title=user["job_title"],
                    email=user["email"],
                )
                if user["title"]:
                    user_watcher.title = user["title"]["name"]
                self.user_watchers.append(user_watcher)

        if not hasattr(self, "_change_events"):
            setattr(self, "_change_events", List[ChangeEvent])
        self._change_events: List[ChangeEvent] = list()
        if not hasattr(self, "_comments"):
            setattr(self, "_comments", List[Comment])
        self._comments: List[Comment] = list()

        if not hasattr(self, "_events"):
            setattr(self, "_events", List[TicketEvent])
        self._events: List[TicketEvent] = list()

        for event in result["data"]["events"]:
            user = None

            comment_event = None
            change_event = None
            changes = None

            event_created_at = event["created_at"]

            if event["created_by_user"]:
                user = User(
                    user_id=event["created_by_user"]["id"],
                    first_name=event["created_by_user"]["first_name"],
                    last_name=event["created_by_user"]["last_name"],
                    job_title=event["created_by_user"]["job_title"],
                    email=event["created_by_user"]["email"],
                )
                if event["created_by_user"]["title"]:
                    user.title = event["created_by_user"]["title"]["name"]

            if event["event_changes"]:
                changes = []
                for change in event["event_changes"]:
                    changes.append(
                        Change(
                            from_value=change["from_value"],
                            to_value=change["to_value"],
                            name=change["name"],
                        )
                    )
                change_event = ChangeEvent(
                    created_by_user=user,
                    created_at=event_created_at,
                    changes=changes,
                    visible_to_customer=event["visible_to_customer"],
                    comment=str(event["comment"]),
                )
                self._change_events.append(change_event)
                self._events.append(change_event)

                if event["comment"] and event["comment"].strip() != "":
                    comment_event = Comment(
                        created_by_user=user,
                        comment=event["comment"],
                        visible_to_customer=event["visible_to_customer"],
                        created_at=event_created_at,
                    )
                    self._comments.append(comment_event)
            else:
                comment_event = Comment(
                    created_by_user=user,
                    comment=event["comment"],
                    visible_to_customer=event["visible_to_customer"],
                    created_at=event_created_at,
                )
                self._comments.append(comment_event)
                self._events.append(comment_event)

        # Sort by datetime created.
        self._events = sorted(self._events, key=lambda x: x.created_at, reverse=True)
        self._change_events = sorted(
            self._change_events, key=lambda x: x.created_at, reverse=True
        )
        self._comments = sorted(
            self._comments, key=lambda x: x.created_at, reverse=True
        )

        if not self.user_watchers:
            self.user_watchers = []

        # self.email_watchers = [email for email in result["data"]["email_watcher_emails"]]

        # Update available buttons

    def create(self) -> "Ticket":
        # If the ticket already exists just return.
        if self.ticket_id:
            self._update()
            return self

        url = self._base_url + "/api/v1/tickets.json?" + self._token

        if not self.priority:
            self.priority = self.config.get()["ticket-priority"]["very-low"]

        if not self.user_watchers:
            self.user_watchers = []

        params = {
            "ticket": {
                "project_id": self.project_id,
                "type_id": self.type.type_id,
                "workspace_id": self.workspace_id,
                "account_vp": 1,
                "subject": str(self.subject),
                "description": str(self.description),
                "visible_to_customer": self.visible_to_customer,
                "priority_id": self.priority,
                "assignee_vp": self.assignee,
                "user_watchers": [user.user_id for user in self.user_watchers],
                "custom_fields_attributes": {
                    str(key): value
                    for key, value in enumerate(self.custom_fields_attributes)
                }
                # Not supported yet
                # "email_watcher_emails": self.email_watchers,
                # 0 -> Security related
                # 1 -> SAP SID
                # 2 -> Category [363 -> Other]
            }
        }

        if self.related_tickets:
            params["ticket"]["related_tickets"] = self.related_tickets

        # for custom_field in self.custom_fields:
        #     params["ticket"][custom_field] = self.custom_fields[custom_field]

        response = requests.post(url, json=params, headers=self.headers)
        # print(response.text)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()

        result = json.loads(response.text)

        self.ticket_id = str(result["data"]["id"])
        self._update()
        return self

    @property
    def comments(self):
        if not hasattr(self, "_comments"):
            self._update()
        return self._comments

    @property
    def change_events(self):
        if not hasattr(self, "_change_events"):
            self._update()
        return self._change_events

    @property
    def events(self):
        if not hasattr(self, "_events"):
            self._update()
        return self._events

    @property
    def custom_fields(self):
        if not hasattr(self, "_custom_fields"):
            self._update()
        return self._custom_fields

    @property
    def related_tickets(self):
        if not hasattr(self, "_related_tickets"):
            self._update()
        return self._related_tickets

    def add_user_watcher_by_id(self, user_id: int, update: bool = True) -> None:
        self.user_watchers.append(
            User(user_id=user_id, first_name=None, last_name=None, email=None)
        )
        if update:
            self.update()

    def update(self, comment: Optional[str] = None):
        url = (
            self._base_url
            + "/api/v1/tickets/"
            + self.ticket_id
            + ".json?"
            + self._token
        )

        payload = {
            "ticket": {
                "subject": str(self.subject),
                "description": str(self.description),
                "priority_id": self.priority,
                "user_watchers": [user.user_id for user in self.user_watchers],
                "custom_fields_attributes": {
                    str(key): value
                    for key, value in enumerate(self.custom_fields_attributes)
                },
                "assignee_vp": str(self.assignee),
                "status_id": self.status.status_id,
                "workspace_id": self.workspace_id,
                "project_id": self.project_id,
                "visible_to_customer": self.visible_to_customer,
            },
            "ticket_event": {"comment": None},
        }

        # for custom_field in self.custom_fields:
        #     payload["ticket"][custom_field] = self.custom_fields[custom_field]

        if comment:
            payload["ticket_event"] = {"comment": str(comment)}

        response = requests.patch(url, json=payload)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()

    def get(self) -> Dict[str, object]:
        url = (
            self._base_url
            + "/api/v1/tickets/"
            + self.ticket_id
            + ".json?"
            + self._token
        )

        selection = [
            "subject",
            "description",
            "priority.name",
            "status.name",
            "events.event_changes.name",
            "customer_user.*",
            "type.name",
            "events.comment",
            "events.created_by_user.first_name",
            "events.created_by_user.last_name",
            "events.created_by_user.title",
            "events.created_by_user.job_title",
            "events.created_by_user.email",
            "events.created_at",
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
            "events.event_changes.to_value",
            "events.event_changes.from_value",
            "events.visible_to_customer",
        ]

        payload = "&select="
        payload += ",".join(selection)
        payload += ",*"
        response = requests.get(url + payload)

        # print(payload)
        # print(response.text)

        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        return json.loads(response.text)

    def comment(self, description: str) -> None:
        url = (
            self._base_url
            + "/api/v1/tickets/"
            + self.ticket_id
            + ".json?"
            + self._token
        )

        payload = {
            "ticket": {
                "workspace_id": self.workspace_id,
                "project_id": self.project_id,
                "visible_to_customer": self.visible_to_customer
            },
            "ticket_event": {"comment": str(description)},
        }

        response = requests.patch(url, json=payload)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def press_button(self, button_name: str, comment: str = None):
        if not self.available_buttons or len(self.available_buttons) == 0:
            self._update_buttons()

        for button in self.available_buttons:
            if button_name == button.name:

                if button.require_comment and not comment:
                    raise ButtonRequiresComment("This button requires a comment")
                url = self._build_url(button.button_id)
                params = {}

                if comment:
                    params = {"comment": str(comment)}
                response = requests.post(url, params)
                if response.status_code != 200:
                    raise HTTPError(response.text)
                response.raise_for_status()
                self._update()
                break
        else:
            raise ButtonNotAvailable("This button is currently not active!")

    def bump_priority_up(self):
        changed = False
        # Current priority + 1
        if self.priority == 33:
            self.priority = 4
            changed = True
        elif self.priority - 1 >= 1:
            self.priority = self.priority - 1
            changed = True

        if changed:
            self.update()

    def bump_priority_down(self):
        changed = False

        # low priority
        if self.priority + 1 <= 4:
            self.priority = self.priority + 1
            changed = True
        elif self.priority == 4:
            self.priority = 33
            changed = True

        if changed:
            self.update()

    def _build_url(self, button):
        url = (
            self._base_url
            + "/api/v1/tickets/"
            + self.ticket_id
            + "/buttons/"
            + str(button)
            + ".json?"
            + self._token
        )
        return url

    def get_text_description(self):
        soup = BeautifulSoup(str(self.description), features="html.parser")
        return soup.get_text()
