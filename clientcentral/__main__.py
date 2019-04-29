#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clientcentral.query as operators
import clientcentral.ticketformatting as tf
from clientcentral.clientcentral import ClientCentral
from model.Status import Status

if __name__ == "__main__":
    cc = ClientCentral(production=False)
    # Dummy commit 10
    # tickets = [cc.get_ticket_by_id("75651")]
    # ,operators.comparison("status.name", "=","'New'")
    # operators.comparison("created_by_user.email", "=",
    #                      "'thomas@labs.epiuse.com'")
    tickets = cc.query_tickets().filter_by(
        operators.and_(operators.comparison("status.closed","=","true"), operators.comparison("workspace_id", "=", "87"))).all()

    for ticket in tickets:
        print(ticket.__dict__)
        #print(ticket.type.name, ticket.type.type_id)

        # ticket.refresh()

        for comment in ticket.comments:
            if comment.created_by_user:
                print("Comment from: " + comment.created_by_user.name +
                      " says: " + comment.comment)
        for change_event in ticket.change_events:
            if change_event.created_by_user:
                print("Change by: " + str(change_event.created_by_user.name))
            for change in change_event.changes:
                print("Changed: " + str(change.name) + " from: " +
                      str(change.from_value) + " to: " + str(change.to_value))

        # ticket.status = Status(
        #     status_id=cc.config.get()["ticket-status"]["cancelled"])
        # ticket.priority = cc.config.get()["ticket-priority"]["very-low"]
        # ticket.update()
        #
        # print("Updated")
