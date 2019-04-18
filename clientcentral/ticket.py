#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import List

import requests

from clientcentral.config import Config
from model.Change import Change
from model.ChangeEvent import ChangeEvent
from model.Comment import Comment
from model.Status import Status
from model.TicketEvent import TicketEvent
from model.User import User


class Ticket:
    _production: bool = False

    _base_url = None
    _token = None

    subject: str = None
    priority: int = None
    ticket_id: str = None
    owner = None
    description: str = None

    created_at: datetime = None
    updated_at: datetime = None

    user_watchers: List[User] = None
    # email_watchers = None

    comments: List[Comment] = None
    events: List[TicketEvent] = None
    change_events: List[ChangeEvent] = None

    status: Status = None
    assignee = None

    config: Config = None
    button_ids = None

    sid = None

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self, base_url, token, config: Config, ticket_id,
                 production: bool):

        self.created_at = None
        self.updated_at = None

        self.comments = []
        self.user_watchers = []

        self._production = production
        self._base_url = base_url
        self._token = token
        self.ticket_id = ticket_id

        self.config = config

        self.button_ids = self.config.get()["button-ids"]

        if ticket_id and not self.created_at:
            self._update()

    def refresh(self):
        self._update()

    def _update(self):
        result = self.get()

        self.description = result["data"]["description"]
        self.subject = result["data"]["subject"]

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

        try:
            self.assignee = result["data"]["assignee"]["id"]
        except TypeError:
            pass

        self.user_watchers = [
            User(user_id=user["id"], name=user["name"], email=user["email"])
            for user in result["data"]["user_watchers"]
        ]

        if not self.comments:
            self.comments = []
        if not self.events:
            self.events = []
        if not self.change_events:
            self.change_events = []

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
                    changes=changes)
                self.change_events.append(change_event)
                self.events.append(change_event)
            else:
                comment_event = Comment(
                    created_by_user=user,
                    description=event["comment"],
                    created_at=event_created_at)
                self.comments.append(comment_event)
                self.events.append(comment_event)

        # Sort by datetime created.
        self.events = sorted(
            self.events, key=lambda x: x.created_at, reverse=True)
        self.change_events = sorted(
            self.change_events, key=lambda x: x.created_at, reverse=True)
        self.comments = sorted(
            self.comments, key=lambda x: x.created_at, reverse=True)

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
                "project_id":
                8,
                "type_id":
                8,
                "workspace_id":
                self.config.get()["ticket-workspace"]["managed-services"],
                "account_vp":
                1,
                "subject":
                str(self.subject),
                "description":
                str(self.description),
                "visible_to_customer":
                True,
                "priority_id":
                self.priority,
                "assignee":
                str(self.assignee),

                # Prod
                # Tiaan S, Jaco K, Thomas S, Tihan P, Marin P
                # "user_watchers": [6, 52, 14012, 14015, 11122]
                "user_watchers": [user.user_id for user in self.user_watchers],

                # Not supported yet
                # "email_watcher_emails": self.email_watchers,

                # 0 -> Security related
                # 1 -> SAP SID
                # 2 -> Category [363 -> Other]
            }
        }

        if self._production:
            params["ticket"]["custom_fields_attributes"] = {
                "0": {
                    "values": 0,
                    "id": 17
                },
                "1": {
                    "values": str(self.sid),
                    "id": 144
                },
                "2": {
                    "values": 363,
                    "id": 75
                }
            }

        response = requests.post(url, json=params, headers=self.headers)
        response.raise_for_status()

        result = json.loads(response.text)

        self.ticket_id = str(result["data"]["id"])
        self._update()
        return self

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
                "user_watchers": [user.user_id for user in self.user_watchers]
            },
            "ticket_event": {
                "comment": str(comment)
            }
        }

        if self._production:
            payload["ticket"]["custom_fields_attributes"] = {
                "0": {
                    "values": 0,
                    "id": 17
                },
                "1": {
                    "values": str(self.sid),
                    "id": 144
                },
                "2": {
                    "values": 363,
                    "id": 75
                }
            }

        response = requests.patch(url, json=payload)
        response.raise_for_status()

    def update(self):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self._token

        payload = {
            "ticket": {
                "subject": str(self.subject),
                "description": str(self.description),
                "priority_id": self.priority,
                "user_watchers": [user.user_id for user in self.user_watchers]
            },
            "ticket_event": {
                "comment": None
            }
        }
        if self._production:
            payload["ticket"]["custom_fields_attributes"] = {
                "0": {
                    "values": 0,
                    "id": 17
                },
                "1": {
                    "values": str(self.sid),
                    "id": 144
                },
                "2": {
                    "values": 363,
                    "id": 75
                }
            }

        response = requests.patch(url, json=payload)
        response.raise_for_status()

    def get(self):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self._token
        payload = "&select=events.comment,events.created_by_user.email,events.created_by_user.name,events.created_at,created_by_user.email,created_by_user.name,subject,description,priority.name,events.comment,user_watchers.email,user_watchers.name,status.name,events.event_changes.change_type,events.event_changes.to_value,events.event_changes.from_value,events.event_changes.name,*"
        response = requests.get(url + payload)
        print(response.text)

        response.raise_for_status()
        return json.loads(response.text)

    def comment(self, description):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + "/buttons/" + str(
            self.button_ids["comment"]) + ".json?" + self._token

        params = {
            'comment': str(description),
        }

        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def grab(self):
        url = self._build_url(self.button_ids["grab"])
        params = {}
        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def cancel_ticket(self, description):
        url = self._build_url(self.button_ids["cancel-ticket"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def request_information(self, description):
        url = self._build_url(self.button_ids["request-information"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def provide_information(self, description):
        url = self._build_url(self.button_ids["provide-information"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def accept(self, description):
        url = self._build_url(self.button_ids["accept"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def decline(self, description):
        url = self._build_url(self.button_ids["decline"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def suggest_solution(self, description):
        url = self._build_url(self.button_ids["suggest-solution"])
        params = {
            'comment': str(description),
        }
        response = requests.post(url, params)
        response.raise_for_status()
        self._update()

    def _build_url(self, button):
        url = self._base_url + "/api/v1/tickets/" + self.ticket_id + "/buttons/" + str(
            button) + ".json?" + self._token
        return url
