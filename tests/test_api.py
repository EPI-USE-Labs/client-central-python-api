import pytest

import asyncio
import clientcentral.query as operators

from clientcentral.clientcentral import ClientCentral
from clientcentral.model.Status import Status
from clientcentral.Exceptions import (
    ButtonNotAvailable,
    ButtonRequiresComment,
    HTTPError,
)

cc = ClientCentral(production=False)
pytest.ticket_id = None

pytest.ticket_id_related = None


def test_get_all_roles():
    r1 = cc.get_roles_manager()
    r2 = cc.get_roles_manager()

    # Test object reuse
    assert r1 == r2

    all_roles = r1.roles

    users_in_role = r1.get_all_users_in_role("IT Support")

    for user in users_in_role:
        print(user)

    # Test get role by nameserver
    role = r1.get_role_by_name("IT Support")

    assert role.role_name == "IT Support"
    assert role.role_id is not None


def test_get_user_by_id():
    um1 = cc.get_users_client()
    um2 = cc.get_users_client()

    # Test object reuse
    assert um1 == um2

    user = um1.get_user_by_id(6)

    print(user)


def test_create_ticket():
    subj = "[Test-Ticket]"
    desc = "<div><h1>This is a test ticket. Please ignore</h1><div>"
    # sid = "ZZZ"

    ticket = cc.create_ticket(
        subject=subj,
        description=desc,
        account_vp=1,
        customer_user_vp=14012,
        project_id=8,
        workspace_id=141,
        type_id=8,
        priority=33,
        custom_fields_attributes=[{"id": 17, "values": 0}, {"id": 75, "values": 363}],
    )
    ticket.refresh()

    # 0 -> Security related
    # 1 -> SAP SID
    # 2 -> Category [363 -> Other]

    assert ticket.run_async is False

    assert ticket.workspace_id == 141
    assert ticket.project_id == 8

    assert desc in ticket.description
    assert ticket.subject == subj
    # assert ticket.sid == sid
    assert ticket.custom_fields["ms_category"]["id"] == 363
    assert ticket.owner.user_id == 14012  # Thomas Scholtz
    assert ticket.creator.user_id == 14012  # Thomas Scholtz
    assert ticket.status.status_id == 1  # New
    assert ticket.status.name == "New"
    assert ticket.status.open is True
    assert ticket.status.closed is False
    assert ticket.priority == 33  # Very low

    pytest.ticket_id = ticket.ticket_id


def test_human_url():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    assert str(ticket.ticket_id) in ticket.get_human_url()


def test_update_ticket():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.description = "<p>update desc 3</p>"
    ticket.commit()
    print(ticket.description)
    assert ticket.get_text_description() == "\nupdate desc 3\n\n"
    assert ticket.description == "<div><br>update desc 3<br><br></div>"


def test_comment():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    old_num_comments = len(ticket.comments)
    old_num_change_events = len(ticket.change_events)

    ticket.comment("<p>Test comment via button</p>")

    ticket.refresh()

    for comment in ticket.comments:
        print(comment.comment)

    for change_event in ticket.change_events:
        for change in change_event.changes:
            print(
                "Changed: "
                + str(change.name)
                + " from: "
                + str(change.from_value)
                + " to: "
                + str(change.to_value)
                + " at: "
                + change_event.created_at.strftime("%B %d, %Y %M %F %s")
            )

    new_num_comments = len(ticket.comments)
    new_num_change_events = len(ticket.change_events)

    assert (old_num_comments + 1) == new_num_comments
    assert (
        ticket.comments[0].comment == "<div><br>Test comment via button<br><br></div>"
    )

    # nothing else should have changed unless someone edited the ticket.
    # or if Client Central executes a workflow
    assert old_num_change_events <= new_num_change_events


def test_set_priority():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)

    ticket.priority = 1
    ticket.commit()
    ticket.refresh()

    assert ticket.priority == 1

    ticket.priority = 33
    ticket.commit()
    ticket.refresh()

    assert ticket.priority == 33


# def test_bump_priority():
#     ticket = cc.get_ticket_by_id(pytest.ticket_id)
#
#     ticket.bump_priority_up()
#     ticket.bump_priority_up()
#     ticket.bump_priority_up()
#     ticket.bump_priority_up()
#     ticket.bump_priority_up()
#     ticket.bump_priority_up()
#     assert ticket.priority == 1
#
#     ticket.bump_priority_down()
#     ticket.bump_priority_down()
#     ticket.bump_priority_down()
#     ticket.bump_priority_down()
#     ticket.bump_priority_down()
#     ticket.bump_priority_down()
#     assert ticket.priority == 33


def test_new_bug():
    tickets = (
        cc.query_tickets()
        .filter_by(
            operators.and_(
                operators.statement("status.open"),
                operators.comparison("workspace_id", "=", "87"),
            )
        )
        .all()
    )


def test_grab():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.press_button("Grab")
    assert ticket.assignee == "User:" + str(14012)  # Thomas Scholtz
    assert ticket.status.status_id == 2  # In progress
    assert ticket.status.name == "In progress"
    print(ticket.ticket_id)
    print(ticket.change_events)
    print(ticket.change_events[0].changes)
    print(ticket.change_events[1].changes)
    # Timing on CC automated changes messes up this test.
    # assert ticket.change_events[0].changes[1].name == "status"
    # assert ticket.change_events[0].changes[1].to_value == str(2)


def test_suggest_solution():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.press_button("Suggest solution", "<p>sol</p>")
    assert ticket.status.status_id == 8  # Suggest solution

    assert ticket.change_events[0].changes[0].name == "status"
    assert ticket.change_events[0].changes[0].to_value == str(8)  # Suggest solution


def test_comment_and_update():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.description = "<p>update desc 2</p>"
    ticket.commit("comment and update")
    ticket.refresh()
    assert ticket.description == "<div><br>update desc 2<br><br></div>"
    assert ticket.get_text_description() == "\nupdate desc 2\n\n"

    last_comment = ticket.comments[0].comment
    assert last_comment == "comment and update"


def test_suggest_solution_then_grab():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    with pytest.raises(ButtonNotAvailable):
        ticket.press_button("Suggest solution", "sol")
    with pytest.raises(ButtonNotAvailable):
        ticket.press_button("Grab")


def test_button_press_comment_required():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    with pytest.raises(ButtonRequiresComment):
        ticket.press_button("Decline")


def test_decline_solution():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.press_button("Decline", "<p>decline</p>")

    assert ticket.status.status_id == 2  # In progress
    assert ticket.change_events[0].changes[0].name == "status"
    assert ticket.change_events[0].changes[0].from_value == str(8)  # Suggest solution
    assert ticket.change_events[0].changes[0].to_value == str(2)  # In progress


def test_lazy_load_get_by_id():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)

    assert ticket is not None

    assert hasattr(ticket, "_comments") == True
    assert hasattr(ticket, "_change_events") == True
    assert hasattr(ticket, "_events") == True


def test_lazy_load():
    import clientcentral.query as operators

    print(pytest.ticket_id)
    ticket = (
        cc.query_tickets()
        .filter_by(
            operators.and_(
                operators.comparison(
                    "created_by_user.email", "=", "'thomas@labs.epiuse.com'"
                ),
                operators.comparison("id", "=", str(pytest.ticket_id)),
            )
        )
        .all()[0]
    )
    assert ticket is not None
    assert ticket.status.open == True
    assert ticket.status.closed == False

    assert hasattr(ticket, "_comments_attribute") == False
    assert hasattr(ticket, "_change_events_attribute") == False
    assert hasattr(ticket, "_events_attribute") == False
    assert hasattr(ticket, "_custom_fields_attribute") == False
    assert hasattr(ticket, "_available_buttons_attribute") == False

    ticket.comments

    assert hasattr(ticket, "_comments_attribute") == True
    assert hasattr(ticket, "_change_events_attribute") == True
    assert hasattr(ticket, "_events_attribute") == True
    assert hasattr(ticket, "_custom_fields_attribute") == True
    assert hasattr(ticket, "_available_buttons_attribute") == True

    assert "<" not in ticket.comments[0].get_comment_text()
    assert ">" not in ticket.comments[0].get_comment_text()


def test_button_press_from_ticket_query():
    import clientcentral.query as operators

    ticket = (
        cc.query_tickets()
        .filter_by(
            operators.and_(
                operators.comparison(
                    "created_by_user.email", "=", "'thomas@labs.epiuse.com'"
                ),
                operators.comparison("id", "=", str(pytest.ticket_id)),
            )
        )
        .all()[0]
    )
    assert ticket is not None
    assert ticket.available_buttons is not None


def test_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.press_button("Cancel ticket", "<p>close</p>")

    assert ticket.status.status_id == 12  # Cancelled


def test_add_user_watcher():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.add_user_watcher_by_id(12)

    # print(ticket.user_watchers)

    assert ticket.user_watchers[0].user_id == 12
    ticket.add_user_watcher_by_id(13, False)
    ticket.refresh()
    assert len(ticket.user_watchers) == 1

    # Test adding an email watcher
    # ticket.add_user_watcher_by_email("test@example.com")
    # ticket.refresh()
    # assert ticket.user_watchers[1].email == "test@example.com"


def test_assignee_user_by_id():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    assert ticket.assignee == "User:14012"
    ticket.assignee = "User:14012"
    ticket.commit()
    assert ticket.assignee == "User:14012"


def test_create_related_ticket():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a related test ticket. Please ignore</h1>"
    # sid = "ZZZ"

    ticket = cc.create_ticket(
        subject=subj,
        description=desc,
        account_vp=1,
        customer_user_vp=14012,
        project_id=8,
        type_id=8,
        workspace_id=141,
        priority=33,
        custom_fields_attributes=[{"id": 17, "values": 0}, {"id": 75, "values": 363}],
        related_tickets=[int(pytest.ticket_id)],
    )
    ticket.refresh()

    assert ticket.workspace_id == 141
    assert ticket.project_id == 8

    assert ticket.description == "<h1>This is a related test ticket. Please ignore</h1>"
    assert ticket.subject == subj
    # assert ticket.sid == sid
    assert ticket.custom_fields["ms_category"]["id"] == 363
    assert ticket.owner.user_id == 14012  # Thomas Scholtz
    assert ticket.owner.resource_owner_id == 13962 # Thomas Scholtz
    assert ticket.creator.user_id == 14012  # Thomas Scholtz
    assert ticket.status.status_id == 1  # New
    assert ticket.status.name == "New"
    assert ticket.status.open == True
    assert ticket.status.closed == False
    assert ticket.priority == 33  # Very low

    pytest.ticket_id_related = ticket.ticket_id

    orig_ticket = cc.get_ticket_by_id(pytest.ticket_id)

    orig_ticket.refresh()
    ticket.refresh()
    assert orig_ticket.related_tickets[0] == int(ticket.ticket_id)
    assert ticket.related_tickets[0] == int(orig_ticket.ticket_id)

    ticket.commit()
    assert orig_ticket.related_tickets[0] == int(ticket.ticket_id)
    assert ticket.related_tickets[0] == int(orig_ticket.ticket_id)
    ticket.status = Status("12")
    ticket.commit()

    ticket.related_tickets.clear()
    ticket.commit()

    orig_ticket.refresh()
    assert len(orig_ticket.related_tickets) == 0

    ticket.related_tickets.append(pytest.ticket_id)
    ticket.commit()

    # When adding a ticket as related and then commenting on the ticket, sometimes the related ticket is removed from the related_tickets list.
    ticket.commit(comment="This is a comment")

    orig_ticket.refresh()
    ticket.refresh()
    assert len(orig_ticket.related_tickets) == 1
    assert ticket.related_tickets[0] == int(orig_ticket.ticket_id)
    assert orig_ticket.related_tickets[0] == int(ticket.ticket_id)



def test_internal_event():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a related test ticket. Please ignore</h1>"
    # sid = "ZZZ"

    ticket = cc.create_ticket(
        subject=subj,
        description=desc,
        account_vp=1,
        customer_user_vp=14012,
        project_id=8,
        type_id=8,
        workspace_id=141,
        priority=33,
        internal=False,
        custom_fields_attributes=[
            {"id": 17, "values": 0},
            {"id": 75, "values": 363},
            {"id": 257, "values": [704]},
        ],
    )

    ticket.commit("not visible", commit_internal=True)
    # assert ticket.events[0].internal is True

    ticket.commit("visible", commit_internal=False)
    # assert ticket.events[0].internal is False

    for event in ticket.events:
        if "not visible" in event.comment:
            assert event.internal is True
        elif "visible" in event.comment:
            assert event.internal is False


def test_internal_event_ticket_not_visible():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a not visible to customer test ticket. Please ignore</h1>"
    # sid = "ZZZ"

    ticket = cc.create_ticket(
        assignee="User:14012",
        account_vp=1,
        customer_user_vp=14012,
        subject=subj,
        description=desc,
        project_id=8,
        type_id=8,
        workspace_id=141,
        priority=33,
        internal=False,
        custom_fields_attributes=[
            {"id": 17, "values": 0},
            {"id": 75, "values": 363},
            {"id": 257, "values": [704]},
        ],
    )

    ticket_id = ticket.ticket_id

    ticket.commit("not visible", False)
    assert ticket.events[0].internal is False
    ticket.commit("visible", True)
    assert ticket.events[0].internal is True

    ticket = cc.get_ticket_by_id(ticket_id)
    ticket.commit("default value")
    assert ticket.events[0].internal is False
    ticket.commit("default value")
    assert ticket.events[0].internal is False


def test_query_internal_event():
    import clientcentral.query as operators

    ticket = (
        cc.query_tickets()
        .filter_by(
            operators.and_(
                operators.comparison(
                    "created_by_user.email", "=", "'thomas@labs.epiuse.com'"
                ),
                operators.comparison("workspace_id", "=", 141),
            )
        )
        .all()[1]
    )

    assert ticket.assignee is not None
    assert ticket.status is not None
    assert ticket.type is not None
    assert ticket.workspace_id is not None
    
    original_ticket_assignee = ticket.assignee

    ticket.commit("not visible", commit_internal=True)
    # ticket.refresh()
    assert ticket.events[0].internal is True
    assert ticket.assignee is not None
    assert ticket.assignee == original_ticket_assignee

    ticket.commit("visible", commit_internal=False)
    # ticket.refresh()
    assert ticket.events[0].internal is False
    assert ticket.assignee is not None
    assert ticket.assignee == original_ticket_assignee


def test_exception_with_unicode_and_missing_payload():
    with pytest.raises(HTTPError) as excinfo:
        raise HTTPError(
            "UNICODE",
            {
                "json": "∀ 	∁ 	∂ 	∃ 	∄ 	∅ 	∆ 	∇ 	∈ 	∉ 	∊ 	∋ 	∌ 	∍ 	∎ 	∏",
                "a": "∀ 	∁ 	∂ 	∃ 	∄ 	∅ 	∆ 	∇ 	∈ 	∉ 	∊ 	∋ 	∌ 	∍ 	∎ 	∏",
                "method": "∀ 	∁ 	∂ 	∃ 	∄ 	∅ 	∆ 	∇ 	∈ 	∉ 	∊ 	∋ 	∌ 	∍ 	∎ 	∏",
            },
            token="MYSECRETTOKEN"
        )
    assert "URL called:" in str(excinfo.value) and "None" in str(excinfo.value)


def test_ensure_multiple_tickets_dont_use_same_attributes():
    subj = "[Test-Ticket]"
    desc = "<div><h1>This is a test ticket. Please ignore</h1><div>"
    # sid = "ZZZ"

    ticket = cc.create_ticket(
        subject=subj,
        description=desc,
        account_vp=1,
        customer_user_vp=14012,
        project_id=8,
        workspace_id=141,
        type_id=8,
        priority=33,
        custom_fields_attributes=[{"id": 17, "values": 0}, {"id": 75, "values": 363}],
    )
    ticket.refresh()

    # 0 -> Security related
    # 1 -> SAP SID
    # 2 -> Category [363 -> Other]

    assert ticket.run_async is False

    assert ticket.workspace_id == 141
    assert ticket.project_id == 8

    assert desc in ticket.description
    assert ticket.subject == subj
    # assert ticket.sid == sid
    assert ticket.custom_fields["ms_category"]["id"] == 363
    assert ticket.owner.user_id == 14012  # Thomas Scholtz
    assert ticket.creator.user_id == 14012  # Thomas Scholtz
    assert ticket.status.status_id == 1  # New
    assert ticket.status.name == "New"
    assert ticket.status.open is True
    assert ticket.status.closed is False
    assert ticket.priority == 33  # Very low

    # Change the category
    ticket.custom_fields["ms_category"]["id"] = 364
    ticket.commit()

    ticket2 = cc.create_ticket(
        subject=subj,
        description=desc,
        account_vp=1,
        customer_user_vp=14012,
        project_id=8,
        workspace_id=141,
        type_id=8,
        priority=33,
        custom_fields_attributes=[{"id": 75, "values": 361}],
    )
    # ticket2.refresh()

    # 0 -> Security related
    # 1 -> SAP SID
    # 2 -> Category [363 -> Other]

    assert ticket2.run_async is False

    assert ticket2.workspace_id == 141
    assert ticket2.project_id == 8

    assert desc in ticket2.description
    assert ticket2.subject == subj
    # assert ticket.sid == sid
    assert ticket2.custom_fields["ms_category"]["id"] == 361
    assert ticket2.owner.user_id == 14012  # Thomas Scholtz
    assert ticket2.creator.user_id == 14012  # Thomas Scholtz
    assert ticket2.status.status_id == 1  # New
    assert ticket2.status.name == "New"
    assert ticket2.status.open is True
    assert ticket2.status.closed is False
    assert ticket2.priority == 33  # Very low

    ticket1 = cc.get_ticket_by_id(ticket.ticket_id)
    ticket1.custom_fields_attributes.append({"id": 75, "values": 363})
    ticket1.commit()

    ticket2 = cc.get_ticket_by_id(ticket2.ticket_id)
    ticket2.custom_fields_attributes.append({"id": 17, "values": 0})
    assert ticket2.custom_fields_attributes != ticket1.custom_fields_attributes
    # ticket2.commit()


# Hardcoded test since I am lazy
def test_ticket_created_from_email():
    # 90771
    # Should not raise NoneType exception
    ticket = cc.get_ticket_by_id(90771)

    # Should not raise NoneType exception
    tickets = (
        cc.query_tickets()
        .filter_by(
            operators.and_(
                operators.comparison("id", "=", "90771"),
            )
        )
        .all()
    )


# def test_create_ticket_on_different_workspace():
#     subj = "[Test-Ticket]"
#     desc = "<h1>This is a test ticket. Please ignore</h1>"
#
#     ticket = cc.create_ticket(
#         subject=subj,
#         type_id=1,
#         description=desc,
#         project_id=cc.config.get()["ticket-workspace"]["client-central"]
#         ["projects"]["general-administration"])
#
#     ticket.refresh()
#
#     assert ticket.description == desc
#     assert ticket.subject == subj
#     assert ticket.owner.user_id == cc.config.get(
#     )["user_ids"]["thomas-scholtz"]
#     assert ticket.status.status_id == cc.config.get()["ticket-status"]["new"]
#     assert ticket.status.name == "New"
#     assert ticket.priority == cc.config.get()["ticket-priority"]["very-low"]
#
#     # pytest.ticket_id = ticket.ticket_id
#     ticket.status = cc.config.get()["ticket-status"]["cancelled"]
#     ticket.commit()
#
#     assert ticket.status == cc.config.get()["ticket-status"]["cancelled"]


@pytest.fixture(scope="module")
def close_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    print("teardown ticket")
    ticket.status = 12  # Cancelled
    ticket.commit()
    assert ticket.status.open == False
    assert ticket.status.closed == True
