#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from typing import List

import requests

from clientcentral.config import Config


class Ticket:
    production: bool = False

    base_url = None
    token = None
    production = False

    subject: str = None
    priority: int = None
    ticket_id: str = None
    owner = None
    description: str = None

    user_watchers: List[int] = None
    # email_watchers = None

    status = None
    assignee = None

    config: Config = None
    button_ids = None

    sid = None

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self, base_url, token, config: Config, ticket_id, production: bool):
        self.production = production
        self.base_url = base_url
        self.token = token
        self.ticket_id = ticket_id

        self.config = config

        self.button_ids = self.config.get()["button-ids"]

        if ticket_id and not self.description and not self.subject and not self.priority and not self.user_watchers:
            self._update()

    def refresh(self):
        self._update()

    def _update(self):
        result = self.get()

        self.description = result["data"]["description"]
        self.subject = result["data"]["subject"]

        self.status = result["data"]["status"]["id"]

        self.priority = result["data"]["priority"]["id"]
        self.owner = result["data"]["created_by_user"]["id"]

        try:
            self.assignee = result["data"]["assignee"]["id"]
        except TypeError:
            pass

        self.user_watchers = [
            user["id"] for user in result["data"]["user_watchers"]
        ]

        try:
            self.sid = result["data"]["sap_sid"]
        except KeyError:
            pass
        # self.email_watchers = [email for email in result["data"]["email_watcher_emails"]]

    def create(self):
        # If the ticket already exists just return.
        if self.ticket_id:
            return

        url = self.base_url + "/api/v1/tickets.json?" + self.token

        if not self.priority:
            self.priority = self.config.get()["ticket-priority"]["very-low"]

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
                "user_watchers":
                self.user_watchers,

                # Not supported yet
                # "email_watcher_emails": self.email_watchers,

                # 0 -> Security related
                # 1 -> SAP SID
                # 2 -> Category [363 -> Other]
            }
        }

        if self.production:
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
        print(response.text)
        response.raise_for_status()

        result = json.loads(response.text)

        self.ticket_id = str(result["data"]["id"])
        # print(result)
        return self

    def add_user_watcher(self, user_id):
        self.user_watchers.append(user_id)

    def comment_and_update(self, comment: str):
        if not comment:
            raise Exception

        url = self.base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self.token

        payload = {
            "ticket": {
                "subject": str(self.subject),
                "description": str(self.description),
                "priority_id": self.priority,
                "user_watchers": self.user_watchers
            },
            "ticket_event": {
                "comment": str(comment)
            }
        }

        if self.production:
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
        url = self.base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self.token

        payload = {
            "ticket": {
                "subject": str(self.subject),
                "description": str(self.description),
                "priority_id": self.priority,
                "user_watchers": self.user_watchers
            },
            "ticket_event": {
                "comment": None
            }
        }
        if self.production:
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
        url = self.base_url + "/api/v1/tickets/" + self.ticket_id + ".json?" + self.token

        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.text)

    def comment(self, description):
        url = self.base_url + "/api/v1/tickets/" + self.ticket_id + "/buttons/" + str(
            self.button_ids["comment"]) + ".json?" + self.token

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
        url = self.base_url + "/api/v1/tickets/" + self.ticket_id + "/buttons/" + str(
            button) + ".json?" + self.token
        return url
