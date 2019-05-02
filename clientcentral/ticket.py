#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import List

import requests

from clientcentral.config import Config
from clientcentral.Exceptions import HTTPError
from clientcentral.model import Change
from clientcentral.model import ChangeEvent
from clientcentral.model import Comment
from clientcentral.model import Status
from clientcentral.model.TicketType import TicketType
from clientcentral.model.User import User


class Ticket:
    _production: bool = False

    _base_url = None
    _token = None

    subject: str = None
    priority: int = None
    ticket_id: str = None
    owner: User = None
    description: str = None

    type: TicketType = None

    workspace_id: int = None
    project_id: int = None

    created_at: datetime = None
    updated_at: datetime = None

    user_watchers: List[User] = None
    # email_watchers = None

    # Custom
    internal_it_category = None
    sap_sid = None
    ms_category = None

    custom_fields_attributes: List[dict] = None

    # comments: List[Comment] = None
    # events: List[TicketEvent] = None
    # change_events: List[ChangeEvent] = None

    status: Status = None
    assignee = None

    config: Config = None
    button_ids = None

    sid = None

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self,
                 base_url,
                 token,
                 config: Config,
                 ticket_id,
                 production: bool,
                 workspace_id: int,
                 project_id: int,
                 custom_fields_attributes: List[dict] = [],
                 ticket_type: TicketType = None,
                 created_at: datetime = None,
                 updated_at: datetime = None,
                 status: Status = None,
                 description: str = None,
                 subject: str = None,
                 owner: User = None,
                 user_watchers: List[User] = [],
                 priority=None,
                 assignee=None):

        self.description = description
        self.subject = subject

        self.created_at = created_at
        self.updated_at = updated_at

        # self.events = []
        # self.change_events = []
        # self.comments = []
        self.user_watchers = user_watchers
        self.custom_fields_attributes = custom_fields_attributes

        self.owner = owner
        self.assignee = assignee

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

    def refresh(self):
        self._update()

    def _update(self):
        # print("UPDATED!!!")

        result = self.get()

        self.description = str(result["data"]["description"]).strip()
        self.subject = str(result["data"]["subject"]).strip()

        self.status = Status(
            status_id=result["data"]["status"]["id"],
            name=result["data"]["status"]["name"])

        self.priority = result["data"]["priority"]["id"]
        self.owner = User(
            user_id=result["data"]["created_by_user"]["id"],
            name=result["data"]["created_by_user"]["name"],
            email=result["data"]["created_by_user"]["email"])

        self.created_at = datetime.strptime(result["data"]["created_at"],
                                            "%Y-%m-%dT%H:%M:%S.%f%z")
        self.updated_at = datetime.strptime(result["data"]["updated_at"],
                                            "%Y-%m-%dT%H:%M:%S.%f%z")

        self.project_id = result["data"]["project"]["id"]
        self.workspace_id = result["data"]["workspace"]["id"]

        self.type = TicketType(
            type_id=result["data"]["type"]["id"],
            name=result["data"]["type"]["name"])

        # Will hopefully get updated in future CC builds
        self.custom_fields_attributes = []

        try:
            self.assignee = result["data"]["assignee"]["id"]
        except TypeError:
            pass

        try:
            self.sap_sid = result["data"]["sap_sid"]
        except KeyError:
            pass

        try:
            self.internal_it_category = result["data"]["internal_it_category"][
                "id"]
        except TypeError:
            pass

        try:
            self.ms_category = result["data"]["ms_category"]["id"]
        except TypeError:
            pass

        self.user_watchers = [
            User(user_id=user["id"], name=user["name"], email=user["email"])
            for user in result["data"]["user_watchers"]
        ]

        if not hasattr(self, "_change_events"):
            setattr(self, "_change_events", [])
        if not hasattr(self, "_comments"):
            setattr(self, "_comments", [])
        if not hasattr(self, "_events"):
            setattr(self, "_events", [])

        for event in result["data"]["events"]:
            user = None
            event_created_at = event["created_at"]

            if event["created_by_user"]:
                user = User(
                    user_id=event["created_by_user"]["id"],
                    name=event["created_by_user"]["name"],
                    email=event["created_by_user"]["email"])

            if event["event_changes"]:
                changes = []
                for change in event["event_changes"]:
                    changes.append(
                        Change(
                            from_value=change["from_value"],
                            to_value=change["to_value"],
                            name=change["name"]))
                change_event = ChangeEvent(
                    created_by_user=user,
                    created_at=event_created_at,
                    changes=changes,
                    comment=event["comment"])
                self._change_events.append(change_event)
                self._events.append(change_event)

                if event["comment"] and event["comment"] != "":
                    self._comments.append(change_event)
            else:
                comment_event = Comment(
                    created_by_user=user,
                    comment=event["comment"],
                    created_at=event_created_at)
                self._comments.append(comment_event)
                self._events.append(comment_event)

        # Sort by datetime created.
        self._events = sorted(
            self._events, key=lambda x: x.created_at, reverse=True)
        self._change_events = sorted(
            self._change_events, key=lambda x: x.created_at, reverse=True)
        self._comments = sorted(
            self._comments, key=lambda x: x.created_at, reverse=True)

        if not self.user_watchers:
            self.user_watchers = []

        try:
            self.sid = result["data"]["sap_sid"]
        except KeyError:
            pass
        # self.email_watchers = [email for email in result["data"]["email_watcher_emails"]]

    def create(self):
        # If the ticket already exists just return.
        if self.ticket_id:
            return

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
                "visible_to_customer": True,
                "priority_id": self.priority,
                "assignee": str(self.assignee),
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
            setattr(self, "_comments", [])
            self._update()

        return self._comments

    @property
    def change_events(self):
        if not hasattr(self, "_change_events"):
            setattr(self, "_change_events", [])
            self._update()

        return self._change_events

    @property
    def events(self):
        if not hasattr(self, "_events"):
            setattr(self, "_events", [])
            self._update()

        return self._events

    def add_user_watcher(self, user_id):
        self.user_watchers.append(user_id)

    def comment_and_update(self, comment: str):
        if not comment:
            raise Exception

        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self._token

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
                "status_id": self.status.status_id,
                "workspace_id": self.workspace_id,
                "project_id": self.project_id
            },
            "ticket_event": {
                "comment": str(comment)
            }
        }

        response = requests.patch(url, json=payload)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()

    def update(self):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self._token

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
                "status_id": self.status.status_id,
                "workspace_id": self.workspace_id,
                "project_id": self.project_id
            },
            "ticket_event": {
                "comment": None
            }
        }

        response = requests.patch(url, json=payload)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()

    def get(self):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self._token
        payload = "&select=type.*,events.comment,events.created_by_user.email,events.created_by_user.name,events.created_at,created_by_user.email,created_by_user.name,subject,description,priority.name,events.comment,user_watchers.email,user_watchers.name,status.name,events.event_changes.to_value,events.event_changes.from_value,events.event_changes.name,*"
        response = requests.get(url + payload)
        # print(response.text)

        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        return json.loads(response.text)

    def comment(self, description):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + "/buttons/" + str(
            self.button_ids["comment"]) + ".json?" + self._token

        params = {
            'comment': str(description),
        }

        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def grab(self):
        url = self._build_url(self.button_ids["grab"])
        params = {}
        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def cancel_ticket(self, description):
        url = self._build_url(self.button_ids["cancel-ticket"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def request_information(self, description):
        url = self._build_url(self.button_ids["request-information"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def provide_information(self, description):
        url = self._build_url(self.button_ids["provide-information"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def accept(self, description):
        url = self._build_url(self.button_ids["accept"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def decline(self, description):
        url = self._build_url(self.button_ids["decline"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def suggest_solution(self, description):
        url = self._build_url(self.button_ids["suggest-solution"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        if response.status_code != 200:
            raise HTTPError(response.text)
        response.raise_for_status()
        self._update()

    def _build_url(self, button):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + "/buttons/" + str(
            button) + ".json?" + self._token
        return url
