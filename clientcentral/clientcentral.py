#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List

from clientcentral.config import Config
from clientcentral.query import QueryTickets
from clientcentral.ticket import Ticket


class ClientCentral:
    production: bool = False
    base_url: str = None
    token: str = None

    config: Config = None

    query = None

    def __init__(self, production, token=None):
        self.production = production

        if token:
            self.token = "token=" + str(token)

        self.config = Config(self.production)
        self.base_url = self.config.get()["base-url"]

        self.token = "token=" + str(self.config.get()["token"])

    def query_tickets(self) -> QueryTickets:
        q = QueryTickets(self.base_url, self.token, self.config,
                         self.production)
        return q

    def get_ticket_by_id(self, ticket_id):
        return Ticket(
            base_url=self.base_url,
            token=self.token,
            ticket_id=str(ticket_id),
            config=self.config,
            production=self.production,
            project_id=None,
            workspace_id=None)

    def create_ticket(self,
                      subject,
                      description,
                      project_id,
                      custom_fields_attributes: List[dict] = [],
                      workspace_id=None,
                      priority=None,
                      type_id=8):
        ticket = Ticket(
            base_url=self.base_url,
            token=self.token,
            ticket_id=None,
            config=self.config,
            production=self.production,
            custom_fields_attributes=custom_fields_attributes,
            workspace_id=workspace_id,
            project_id=project_id,
            type_id=type_id)

        ticket.subject = str(subject)
        ticket.description = str(description)
        ticket.priority = priority
        ticket.create()

        return ticket
