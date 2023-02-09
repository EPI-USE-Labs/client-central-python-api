#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
import ujson

# import requests
import aiohttp
import asyncio
from clientcentral.Exceptions import (
    ButtonNotAvailable,
    ButtonRequiresComment,
    HTTPError,
    DateFormatInvalid,
)
from clientcentral.model.Button import Button
from clientcentral.model.Change import Change
from clientcentral.model.ChangeEvent import ChangeEvent
from clientcentral.model.Comment import Comment
from clientcentral.model.Status import Status
from clientcentral.model.TicketEvent import TicketEvent
from clientcentral.model.TicketType import TicketType
from clientcentral.model.User import User

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class Ticket(object):
    def __init__(
        self,
        base_url: str,
        token: str,
        ticket_id: Optional[str],  # Only required when getting a ticket
        production: bool,
        workspace_id: Optional[int],  # Only required for creating tickets
        project_id: Optional[int],  # Only required for creating tickets
        account_vp: Optional[int],  # Only required for creating tickets
        customer_user_vp: Optional[int],  # Only required for creating tickets
        custom_fields_attributes: Optional[List[Dict[str, int]]] = None,
        ticket_type: Optional[TicketType] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        status: Optional[Status] = None,
        description: Optional[str] = None,
        subject: Optional[str] = None,
        owner: Optional[User] = None,
        creator: Optional[User] = None,
        user_watchers: Optional[List[User]] = None,
        # email_watchers: Optional[List[str]] = None,
        priority: Optional[int] = None,
        assignee: Optional[str] = None,
        related_tickets: Optional[List[int]] = None,
        internal: bool = False,
        session=None,
        run_async: bool = False,
    ) -> None:

        self.description = description
        self.subject = subject

        self.created_at = created_at
        self.updated_at = updated_at

        # self.events = []
        # self.change_events = []
        # self.comments = []
        self.user_watchers = [] if user_watchers is None else user_watchers
        # self.email_watchers = [] if email_watchers is None else email_watchers

        self.custom_fields_attributes = (
            [] if custom_fields_attributes is None else custom_fields_attributes
        )

        self._related_tickets_attribute = (
            [] if related_tickets is None else related_tickets
        )

        self.creator = creator
        self.owner = owner

        self.assignee = assignee

        self.internal = internal

        self._production = production
        self._base_url = base_url
        self._token = token
        self.ticket_id = ticket_id

        self.status = status

        self.type = ticket_type

        self.workspace_id = workspace_id
        self.project_id = project_id

        self.priority = priority

        self.account_vp = account_vp
        self.customer_user_vp = customer_user_vp

        self.run_async = run_async
        self.session = session

        self._event_loop = None

        self._net_calls = 0

    @classmethod
    async def factory_create(
        cls,
        base_url: str,
        token: str,
        ticket_id: Optional[str],  # Optional because it's not required for create
        production: bool,
        workspace_id: Optional[
            int
        ],  # Optional because it's not required when getting a ticket
        project_id: Optional[
            int
        ],  # Optional because it's not required when getting a ticket
        account_vp: Optional[
            int
        ],  # Optional because it's not required when getting a ticket
        customer_user_vp: Optional[
            int
        ],  # Optional because it's not required when getting a ticket
        custom_fields_attributes: Optional[List[Dict[str, int]]] = None,
        ticket_type: Optional[TicketType] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        status: Optional[Status] = None,
        description: Optional[str] = None,
        subject: Optional[str] = None,
        owner: Optional[User] = None,
        creator: Optional[User] = None,
        user_watchers: Optional[List[User]] = None,
        priority: Optional[int] = None,
        assignee: Optional[str] = None,
        related_tickets: Optional[List[int]] = None,
        internal: bool = False,
        session=None,
        run_async: bool = False,
    ):
        self = Ticket(
            base_url=base_url,
            token=token,
            ticket_id=ticket_id,
            production=production,
            workspace_id=workspace_id,
            project_id=project_id,
            custom_fields_attributes=custom_fields_attributes,
            ticket_type=ticket_type,
            created_at=created_at,
            updated_at=updated_at,
            status=status,
            description=description,
            subject=subject,
            owner=owner,
            creator=creator,
            user_watchers=user_watchers,
            priority=priority,
            assignee=assignee,
            related_tickets=related_tickets,
            internal=internal,
            session=session,
            run_async=run_async,
            account_vp=account_vp,
            customer_user_vp=customer_user_vp,
        )
        self._event_loop = self._get_event_loop()

        self.session = session
        # if not self.session:
        #     self.session = aiohttp.ClientSession(loop=self._event_loop)

        if self.ticket_id and not self.created_at and not self.updated_at:
            await self._update()
        return self

    def refresh(self) -> "Ticket":
        """Refreshes the current ticket instance. Syncs all data from Client Central"""
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._update())

        if self.run_async:
            return future

        result = self._event_loop.run_until_complete(future)
        return result

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

    async def _update_buttons(self):
        url = (
            self._base_url
            + "/api/v1/tickets/"
            + self.ticket_id
            + "/available_buttons.json?"
            + self._token
        )

        response = await self._request("GET", url)
        if response["status_code"] != 200:
            raise HTTPError(
                "Failed to get ticket available buttons", response, token=self._token
            )

        result = response["json"]

        self._available_buttons_attribute = list()

        for button in result["data"]:
            self._available_buttons_attribute.append(
                Button(
                    button_id=button["id"],
                    enabled=button["enabled"],
                    name=button["name"],
                    agent_only=button["agent_only"],
                    require_comment=button["require_comment"],
                    colour=button["colour"],
                )
            )
        return self._available_buttons_attribute

    # Call the button URL to get the current buttons.
    @property
    def available_buttons(self):
        if not hasattr(self, "_available_buttons_attribute"):
            if self._event_loop is None:
                self._event_loop = self._get_event_loop()

            future = self._event_loop.create_task(self._update_buttons())
            self._event_loop.run_until_complete(future)

        return self._available_buttons_attribute

    async def _update(self) -> "Ticket":
        response = await self._get()
        result: Dict[str, Any] = response["json"]

        self.description = str(result["data"]["description"]).strip()
        self.subject = str(result["data"]["subject"]).strip()

        new_status = Status(
            status_id=result["data"]["status"]["id"],
            name=result["data"]["status"]["name"],
            open=not result["data"]["status"]["closed"],
        )

        if self.status != new_status:
            # Update buttons
            await self._update_buttons()

        self.status = new_status

        self.priority = result["data"]["priority"]["id"]

        self.creator = None
        # If the ticket is created via email there will not be a creator
        if result["data"]["created_by_user"]:
            self.creator = User(
                user_id=result["data"]["created_by_user"]["id"],
                first_name=result["data"]["created_by_user"]["first_name"],
                last_name=result["data"]["created_by_user"]["last_name"],
                job_title=result["data"]["created_by_user"]["job_title"],
                email=result["data"]["created_by_user"]["email"],
            )
            if result["data"]["created_by_user"]["title"]:
                self.creator.title = result["data"]["created_by_user"]["title"]["name"]

        if result["data"]["customer_user"]:
            self.owner = User(
                user_id=result["data"]["customer_user"]["id"],
                first_name=result["data"]["customer_user"]["first_name"],
                last_name=result["data"]["customer_user"]["last_name"],
                job_title=result["data"]["customer_user"]["job_title"],
                email=result["data"]["customer_user"]["email"],
                resource_owner_id=result["data"]["customer_user"]["number"],
            )
            if result["data"]["customer_user"]["title"]:
                self.owner.title = result["data"]["customer_user"]["title"]["name"]

        # Created at
        try:
            self.created_at = datetime.strptime(
                result["data"]["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
        except ValueError:
            pass

        try:
            self.created_at = datetime.strptime(
                result["data"]["created_at"], "%Y-%m-%dT%H:%M:%S%z"
            )
        except ValueError:
            pass

        if self.created_at == None:
            raise DateFormatInvalid(
                "Failed to convert datetime: " + str(result["data"]["created_at"])
            )

        # Updated at
        try:
            self.updated_at = datetime.strptime(
                result["data"]["updated_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
        except ValueError:
            pass

        try:
            self.updated_at = datetime.strptime(
                result["data"]["updated_at"], "%Y-%m-%dT%H:%M:%S%z"
            )
        except ValueError:
            pass

        if self.updated_at == None:
            raise DateFormatInvalid(
                "Failed to convert datetime: " + str(result["data"]["updated_at"])
            )

        self.account_vp = result["data"]["account"]["id"]
        self.customer_user_vp = result["data"]["customer_user"]["id"]

        self.project_id = result["data"]["project"]["id"]
        self.workspace_id = result["data"]["workspace"]["id"]

        self.internal = result["data"]["internal"]

        self.type = TicketType(
            type_id=result["data"]["type"]["id"], name=result["data"]["type"]["name"]
        )

        if result["data"]["assignee"]:
            self.assignee = (
                result["data"]["assignee"]["_type"]
                + ":"
                + str(result["data"]["assignee"]["id"])
            )

        try:
            result["data"]["related_tickets"]
            # self.related_tickets = []
            self._related_tickets_attribute = []
            for related_ticket in result["data"]["related_tickets"]:
                self._related_tickets_attribute.append(int(related_ticket["id"]))
        except KeyError:
            pass

        self._custom_fields_attribute: dict = {}
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
            "internal",
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
                self._custom_fields_attribute[field_name] = result["data"][field_name]

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

        if not hasattr(self, "_change_events_attribute"):
            setattr(self, "_change_events_attribute", List[ChangeEvent])
        self._change_events_attribute: List[ChangeEvent] = list()
        if not hasattr(self, "_comments_attribute"):
            setattr(self, "_comments_attribute", List[Comment])
        self._comments_attribute: List[Comment] = list()

        if not hasattr(self, "_events_attribute"):
            setattr(self, "_events_attribute", List[TicketEvent])
        self._events_attribute: List[TicketEvent] = list()

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
                    internal=event["internal"],
                    comment=str(event["comment"]),
                )
                self._change_events_attribute.append(change_event)
                self._events_attribute.append(change_event)

                if event["comment"] and event["comment"].strip() != "":
                    comment_event = Comment(
                        created_by_user=user,
                        comment=event["comment"],
                        internal=event["internal"],
                        created_at=event_created_at,
                    )
                    self._comments_attribute.append(comment_event)
            else:
                comment_event = Comment(
                    created_by_user=user,
                    comment=event["comment"],
                    internal=event["internal"],
                    created_at=event_created_at,
                )
                self._comments_attribute.append(comment_event)
                self._events_attribute.append(comment_event)

        # Sort by datetime created.
        self._events_attribute = sorted(
            self._events_attribute, key=lambda x: x.created_at, reverse=True
        )
        self._change_events_attribute = sorted(
            self._change_events_attribute, key=lambda x: x.created_at, reverse=True
        )
        self._comments_attribute = sorted(
            self._comments_attribute, key=lambda x: x.created_at, reverse=True
        )

        if not self.user_watchers:
            self.user_watchers = []

        # self.email_watchers = [email for email in result["data"]["email_watcher_emails"]]

        # Update available buttons
        return self

    async def _create(self):
        # If the ticket already exists just return.
        if self.ticket_id:
            return await self._update()

        url = self._base_url + "/api/v1/tickets.json?" + self._token

        if not self.user_watchers:
            self.user_watchers = []

        params = {
            "ticket": {
                "project_id": self.project_id,
                "type_id": self.type.type_id,
                "workspace_id": self.workspace_id,
                "account_vp": self.account_vp,
                "customer_user_vp": self.customer_user_vp,
                "subject": str(self.subject),
                "description": str(self.description),
                "internal": self.internal,
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

        params["ticket"]["related_tickets"] = await self._related_tickets()

        response = await self._request("POST", url, json=params)

        if response["status_code"] != 200:
            raise HTTPError("Failed to create ticket", response, token=self._token)

        self.ticket_id = str(response["json"]["data"]["id"])
        return await self._update()

    async def create(self) -> "Ticket":
        return await self._create()

    async def _comments(self):
        if not hasattr(self, "_comments_attribute"):
            await self._update()
        return self._comments_attribute

    @property
    def comments(self):
        # return await self._comments()
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._comments())

        if self.run_async:
            return future
        return self._event_loop.run_until_complete(future)

    async def _change_events(self):
        if not hasattr(self, "_change_events_attribute"):
            await self._update()
        return self._change_events_attribute

    @property
    def change_events(self):
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._change_events())

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    async def _events(self):
        if not hasattr(self, "_events_attribute"):
            await self._update()
        return self._events_attribute

    @property
    def events(self):
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._events())

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    async def _custom_fields(self):
        if not hasattr(self, "_custom_fields_attribute"):
            await self._update()
        return self._custom_fields_attribute

    @property
    def custom_fields(self):
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._custom_fields())

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    async def _related_tickets(self):
        if not hasattr(self, "_related_tickets_attribute"):
            await self._update()
        return self._related_tickets_attribute

    @property
    def related_tickets(self):
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._related_tickets())

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    # def add_email_watcher(self, email:str, update: bool = True) -> None:
    #     self.email_watchers.append(email)
    #     if update:
    #         self.commit()

    def add_user_watcher_by_id(self, user_id: int, update: bool = True) -> None:
        self.user_watchers.append(
            User(user_id=user_id, first_name=None, last_name=None, email=None)
        )
        if update:
            self.commit()

    async def _commit(
        self,
        comment: Optional[str] = None,
        commit_internal: bool = False,
        disable_notifications: bool = False,
    ):
        if self.ticket_id is None:
            raise Exception("Ticket ID is not set")

        if self.status is None:
            raise Exception("Ticket Status is not set, this is prbably a bug.")

        if self.type is None:
            raise Exception("Ticket Type is not set, this is prbably a bug.")

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
                "customer_user_vp": self.customer_user_vp,
                "account_vp": self.account_vp,
                "status_id": self.status.status_id,
                "workspace_id": self.workspace_id,
                "project_id": self.project_id,
                "type_id": self.type.type_id,
                "internal": self.internal,
                "related_tickets": [
                    int(related_ticket_id)
                    for related_ticket_id in self._related_tickets_attribute
                ],
                # "email_watchers": self.email_watchers,
            },
            "ticket_event": {
                "comment": None,
                "internal": commit_internal,
                "disable_notifications": disable_notifications,
            },
        }

        # for custom_field in self.custom_fields:
        #     payload["ticket"][custom_field] = self.custom_fields[custom_field]

        if comment:
            payload["ticket_event"]["comment"] = str(comment)

        response = await self._request("PATCH", url, json=payload)

        if response["status_code"] != 200:
            raise HTTPError(
                "Failed to add user watcher by user ID", response, token=self._token
            )

        return await self._update()

    def commit(
        self,
        comment: Optional[str] = None,
        commit_internal: bool = False,
        disable_notifications: bool = False,
    ):
        """Commit the current state of the ticket to Client Central"""

        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(
            self._commit(comment, commit_internal, disable_notifications)
        )

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    async def _get(self):
        if self.ticket_id is None:
            raise Exception(
                "Ticket ID is not set, can not retrieve a ticket without an ID."
            )

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
            "status.closed",
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
            "events.internal",
            "assignee",
        ]

        payload = "&select="
        payload += ",".join(selection)
        payload += ",*"

        response = await self._request("GET", url + payload)

        if response["status_code"] != 200:
            raise HTTPError(
                f"Failed to get ticket #{self.ticket_id}", response, token=self._token
            )

        return response

    async def _comment(self, description: str) -> "Ticket":
        if self.ticket_id is None:
            raise Exception("Ticket ID is not set")

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
                "internal": self.internal,
            },
            "ticket_event": {"comment": str(description)},
        }

        response = await self._request("PATCH", url, json=payload)

        if response["status_code"] != 200:
            raise HTTPError(
                f"Failed to comment on ticket #{self.ticket_id}",
                response,
                token=self._token,
            )
        return await self._update()

    def comment(self, description: str) -> None:
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._comment(description))

        if self.run_async:
            return future

        result = self._event_loop.run_until_complete(future)
        return result

    async def _press_button(self, button_name: str, comment: Optional[str] = None):
        if not self.available_buttons or len(self.available_buttons) == 0:
            await self._update_buttons()

        for button in self.available_buttons:
            if button_name == button.name:

                if button.require_comment and not comment:
                    raise ButtonRequiresComment("This button requires a comment")
                url = self._build_url(button.button_id)
                params = {}

                if comment:
                    params = {"comment": str(comment)}

                response = await self._request("POST", url, json=params)
                if response["status_code"] != 200:
                    raise HTTPError(
                        f"Failed to press button on ticket #{self.ticket_id}",
                        response,
                        token=self._token,
                    )
                await self._update()
                break
        else:
            raise ButtonNotAvailable("This button is currently not active!")

    def press_button(self, button_name: str, comment: Optional[str] = None):
        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(self._press_button(button_name, comment))

        if self.run_async:
            return future

        result = self._event_loop.run_until_complete(future)
        return result

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
        soup = BeautifulSoup(
            str(self.description.replace("<br>", "\n")), features="html.parser"
        )
        return soup.get_text()

    def get_human_url(self):
        if self._production:
            return "https://clientcentral.io/support/tickets/" + str(self.ticket_id)
        return "https://qa-cc.labs.epiuse.com/support/tickets/" + str(self.ticket_id)

    def _get_event_loop(self):
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
