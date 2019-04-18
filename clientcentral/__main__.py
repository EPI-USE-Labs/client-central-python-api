#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clientcentral.query as operators
import clientcentral.ticketformatting as tf
from clientcentral.clientcentral import ClientCentral

if __name__ == "__main__":
    cc = ClientCentral(production=False)
    # Dummy commit 10
    #ticket = cc.get_ticket_by_id("78263")
    tickets = cc.query_tickets().filter_by(
        operators.and_(
            operators.comparison("created_by_user.email", "=",
                                 "'thomas@labs.epiuse.com'"),
            operators.comparison("subject", "CONTAINS", "'TICKET SHOULD BE'"),
        )).all()

    for ticket in tickets:
        print(ticket.__dict__)
        for comment in ticket.comments:
            if comment.created_by_user:
                print("Comment from: " + comment.created_by_user.name +
                      " says: " + comment.description)
