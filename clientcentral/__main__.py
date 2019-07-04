#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clientcentral.query as operators
from clientcentral.clientcentral import ClientCentral
from clientcentral.model.Status import Status

if __name__ == "__main__":
    cc = ClientCentral(production=True)
    # Dummy commit 10
    # tickets = [cc.get_ticket_by_id("75705")]
    # ,operators.comparison("status.name", "=","'New'")
    # operators.comparison("created_by_user.email", "=",
    #                      "'thomas@labs.epiuse.com'")
    # tickets = (
    #     cc.query_tickets()
    #     .filter_by(
    #         operators.comparison(
    #             "created_by_user.email", "=", "'thomas@labs.epiuse.com'"
    #         )
    #     )
    #     .all()
    # )

    all_roles = cc.get_roles_manager().get_all_users_in_role("Internal IT - Email")

    print(all_roles)

    for role in all_roles:
        print(role.__dict__)

    # tickets = [cc.get_ticket_by_id("82061")]

    # for ticket in tickets:
    # print(ticket.__dict__)
    # print(ticket.type.name, ticket.type.type_id)

    # ticket.refresh()

    # print(ticket.custom_fields_attributes)

    # for comment in ticket.comments:
    #     if comment.created_by_user:
    #         print(
    #             "Comment from: "
    #             + comment.created_by_user.name
    #             + " says: "
    #             + comment.comment
    #         )
    # for change_event in ticket.change_events:
    #     if change_event.created_by_user:
    #         print("Change by: " + str(change_event.created_by_user.name))
    #     for change in change_event.changes:
    #         print(
    #             "Changed: "
    #             + str(change.name)
    #             + " from: "
    #             + str(change.from_value)
    #             + " to: "
    #             + str(change.to_value)
    #         )

    # ticket.description = '<p>Hi!</p><br/><p>This is the master ticket for the new candidate: <strong id="candidate_name">test user</strong> with the email: <strong id="candidate_email">test@test.co</strong></p><br/><p>Relevant tickets are being/have been created for the relevant On-Boarding access requests. Once all the requests have been completed this ticket will be closed!</p><br/><p>The following tasks need to be <strong>approved/completed</strong>:</p><p><ul id=\'job_list\'><li>l1</li><li>l2</li><li><del>l3</del></li></ul></p><br/><p>Please note that this is an <strong>automated</strong> response.</p><br><p>Kind regards,</p><p>SWAT.</p>'
    # ticket.update()
    # ticket = cc.get_ticket_by_id("75888")
    # print(ticket.description)
    # ticket.status = Status(status_id=cc.config.get()["ticket-status"]["cancelled"])
    # ticket.priority = cc.config.get()["ticket-priority"]["very-low"]
    # ticket.update()
    # #
    # print("Updated")
