#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

from clientcentral.model.TicketType import TicketType
from clientcentral.query import QueryTickets
from clientcentral.roles import Roles
from clientcentral.users_client import UsersClient

from clientcentral.ticket import Ticket

from clientcentral.Exceptions import NoTokenProvided

import os
import asyncio
import aiohttp
import ujson


class ClientCentral:
    def __init__(
        self,
        production: bool,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        run_async: bool = False,
    ) -> None:
        self.production = production

        if base_url is None:
            self.base_url = "https://qa.clientcentral.io"
            if production:
                self.base_url = "https://clientcentral.io"
        else:
            self.base_url = base_url

        # Get the token from the environment
        raw_token = None

        if os.environ.get("CC_TOKEN"):
            raw_token = str(os.environ.get("CC_TOKEN"))

        if token:
            raw_token = token
            self.token = "token=" + raw_token

        if not raw_token or not len(raw_token) >= 32:
            raise NoTokenProvided("Token invalid or not present")

        self.token = "token=" + raw_token

        self.run_async = run_async
        # self._event_loop = None

        self._event_loop = self._get_event_loop()
        future = self._event_loop.create_task(self._create_session())
        self._event_loop.run_until_complete(future)

    async def _create_session(self):
        async with aiohttp.ClientSession(
            loop=self._get_event_loop(), json_serialize=ujson.dumps
        ) as session:
            self.session = session

    def _get_event_loop(self):
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def query_tickets(self) -> QueryTickets:
        q = QueryTickets(self.base_url, self.token, self.production, self.session)
        return q

    def get_ticket_by_id(self, ticket_id: str) -> Ticket:
        future = self._event_loop.create_task(
            Ticket.factory_create(
                session=self.session,
                base_url=self.base_url,
                token=self.token,
                ticket_id=str(ticket_id),
                production=self.production,
                project_id=None,
                workspace_id=None,
                run_async=self.run_async,
                account_vp=None,
                customer_user_vp=None,
            ),
        )

        if self.run_async:
            return future

        result = self._event_loop.run_until_complete(future)
        return result

    async def _create_ticket(
        self,
        subject: str,
        description: str,
        project_id,
        priority,
        type_id: Optional[int],
        account_vp: int,
        customer_user_vp: int,
        custom_fields_attributes: Optional[List[Dict[str, int]]] = None,
        workspace_id=None,
        assignee=None,
        related_tickets: Optional[List[int]] = None,
        internal: bool = False,
    ):

        if type_id is None:
            raise Exception("Ticket type ID is required when creating a ticket")
        else:
            ticket_type = TicketType(type_id=type_id)

        ticket = await Ticket.factory_create(
            session=self.session,
            base_url=self.base_url,
            token=self.token,
            ticket_id=None,
            production=self.production,
            custom_fields_attributes=custom_fields_attributes,
            account_vp=account_vp,
            customer_user_vp=customer_user_vp,
            workspace_id=workspace_id,
            project_id=project_id,
            ticket_type=ticket_type,
            related_tickets=related_tickets,
            assignee=assignee,
            internal=internal,
            run_async=self.run_async,
        )

        ticket.subject = str(subject)
        ticket.description = str(description)
        ticket.priority = priority
        await ticket.create()

        return ticket

    def create_ticket(
        self,
        subject: str,
        description: str,
        project_id,
        priority,
        account_vp: int,
        customer_user_vp: int,
        custom_fields_attributes: Optional[List[Dict[str, int]]] = None,
        workspace_id=None,
        type_id: Optional[int] = None,
        assignee=None,
        related_tickets: Optional[List[int]] = None,
        internal: bool = False,
    ):

        # if self._event_loop is None:
        #     self._event_loop = self._get_event_loop()

        future = self._event_loop.create_task(
            self._create_ticket(
                account_vp=account_vp,
                customer_user_vp=customer_user_vp,
                subject=subject,
                description=description,
                project_id=project_id,
                priority=priority,
                custom_fields_attributes=custom_fields_attributes,
                workspace_id=workspace_id,
                type_id=type_id,
                assignee=assignee,
                related_tickets=related_tickets,
                internal=internal,
            ),
            # loop=self._get_event_loop(),
        )
        if self.run_async:
            return future

        result = self._event_loop.run_until_complete(future)
        return result

    def get_users_client(self) -> UsersClient:
        if not hasattr(self, "_users_client"):
            self._users_client = UsersClient(
                self.base_url, self.token, self.production, self.session
            )
        return self._users_client

    def get_roles_manager(self) -> Roles:
        # Call roles API
        # Going to change in next CC prod.
        if not hasattr(self, "_roles"):
            self._roles = Roles(
                self.base_url, self.token, self.production, self.session
            )
        return self._roles
