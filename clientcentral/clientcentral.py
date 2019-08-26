#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

from clientcentral.config import Config
from clientcentral.model.TicketType import TicketType
from clientcentral.query import QueryTickets
from clientcentral.roles import Roles
from clientcentral.users_manager import UsersManager

from clientcentral.ticket import Ticket

from clientcentral.Exceptions import HTTPError


class ClientCentral:
    production: bool = False
    base_url: str
    token: Optional[str] = None

    config: Config = None

    query = None

    def __init__(self, production: bool, token: Optional[str] = None) -> None:
        self.production = production

        self.config = Config(self.production)
        self.token = "token=" + str(self.config.get()["token"])
        self.base_url = self.config.get()["base-url"]

        if token:
            self.token = "token=" + str(token)


    def query_tickets(self) -> QueryTickets:
        q = QueryTickets(self.base_url, self.token, self.config, self.production)
        return q

    def get_ticket_by_id(self, ticket_id: str) -> Ticket:
        return Ticket(
            base_url=self.base_url,
            token=self.token,
            ticket_id=str(ticket_id),
            config=self.config,
            production=self.production,
            project_id=None,
            workspace_id=None,
        )

    def create_ticket(
        self,
        subject: str,
        description: str,
        project_id,
        priority,
        custom_fields_attributes: List[Dict[str, int]] = [],
        workspace_id=None,
        type_id: Optional[int] = None,
        assignee=None,
        related_tickets: Optional[List[int]] = None,
    ):

        if not type_id:
            ticket_type = TicketType(type_id=8)
        else:
            ticket_type = TicketType(type_id=type_id)

        ticket = Ticket(
            base_url=self.base_url,
            token=self.token,
            ticket_id=None,
            config=self.config,
            production=self.production,
            custom_fields_attributes=custom_fields_attributes,
            workspace_id=workspace_id,
            project_id=project_id,
            ticket_type=ticket_type,
            related_tickets=related_tickets,
            assignee=assignee,
        )

        ticket.subject = str(subject)
        ticket.description = str(description)
        ticket.priority = priority
        ticket.create()

        return ticket

    def get_users_manager(self) -> UsersManager:
        if not hasattr(self, "_users_manager"):
            self._users_manager = UsersManager(
                self.base_url, self.token, self.config, self.production
            )
        return self._users_manager

    def get_roles_manager(self) -> Roles:
        # Call roles API
        # Going to change in next CC prod.
        if not hasattr(self, "_roles"):
            self._roles = Roles(self.base_url, self.token, self.config, self.production)
        return self._roles
