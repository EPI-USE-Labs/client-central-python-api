import pytest

from clientcentral.clientcentral import ClientCentral
from clientcentral.Exceptions import (ButtonNotAvailable,
                                      ButtonRequiresComment, HTTPError)

cc = ClientCentral(production=False)
pytest.ticket_id = None


def test_create_ticket():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a test ticket. Please ignore</h1>"
    # sid = "ZZZ"

    ticket = cc.create_ticket(
        subject=subj,
        description=desc,
        project_id=8,
        workspace_id=16,
        custom_fields_attributes=[{
            "id": 17,
            "values": 0
        }, {
            "id": 75,
            "values": 363
        }])
    ticket.refresh()

    # 0 -> Security related
    # 1 -> SAP SID
    # 2 -> Category [363 -> Other]

    assert ticket.workspace_id == 16
    assert ticket.project_id == 8

    assert ticket.description == desc
    assert ticket.subject == subj
    # assert ticket.sid == sid
    assert ticket.custom_fields["ms_category"]["id"] == 363
    assert ticket.owner.user_id == cc.config.get(
    )["user_ids"]["thomas-scholtz"]
    assert ticket.creator.user_id == cc.config.get(
    )["user_ids"]["thomas-scholtz"]
    assert ticket.status.status_id == cc.config.get()["ticket-status"]["new"]
    assert ticket.status.name == "New"
    assert ticket.priority == cc.config.get()["ticket-priority"]["very-low"]

    pytest.ticket_id = ticket.ticket_id


def test_update_ticket():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.description = "<p>update desc</p>"
    ticket.update()
    assert ticket.description == "<p>update desc</p>"


def test_comment():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    old_num_comments = len(ticket.comments)
    old_num_change_eventes = len(ticket.change_events)

    ticket.comment("<p>Test comment via button</p>")

    ticket.refresh()

    for comment in ticket.comments:
        print(comment.comment)

    for change_event in ticket.change_events:
        for change in change_event.changes:
            print("Changed: " + change.name + " from: " + change.from_value +
                  " to: " + change.to_value + " at: " +
                  change_event.created_at.strftime("%B %d, %Y %M %F %s"))

    new_num_comments = len(ticket.comments)
    new_num_change_events = len(ticket.change_events)

    assert (old_num_comments + 1) == new_num_comments
    assert ticket.comments[0].comment == "<p>Test comment via button</p>"

    # nothing else should have changed unless someone edited the ticket.
    assert (old_num_change_eventes) == new_num_change_events


def test_bump_priority():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)

    ticket.bump_priority_up()
    ticket.bump_priority_up()
    ticket.bump_priority_up()
    ticket.bump_priority_up()
    assert ticket.priority == 1

    ticket.bump_priority_down()
    ticket.bump_priority_down()
    ticket.bump_priority_down()
    ticket.bump_priority_down()
    assert ticket.priority == 33


def test_grab():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.press_button("Grab")
    assert ticket.assignee == cc.config.get()["user_ids"]["thomas-scholtz"]
    assert ticket.status.status_id == cc.config.get(
    )["ticket-status"]["in-progress"]
    assert ticket.status.name == "In progress"
    assert ticket.change_events[0].changes[1].name == "status"
    assert ticket.change_events[0].changes[1].to_value == str(
        cc.config.get()["ticket-status"]["in-progress"])


def test_suggest_solution():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.press_button("Suggest solution", "<p>sol</p>")
    assert ticket.status.status_id == cc.config.get(
    )["ticket-status"]["suggest-solution"]

    assert ticket.change_events[0].changes[0].name == "status"
    assert ticket.change_events[0].changes[0].to_value == str(
        cc.config.get()["ticket-status"]["suggest-solution"])


def test_comment_and_update():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.description = "<p>update desc 2</p>"
    ticket.update("comment and update")
    ticket.refresh()
    assert ticket.description == "<p>update desc 2</p>"

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

    assert ticket.status.status_id == cc.config.get(
    )["ticket-status"]["in-progress"]
    assert ticket.change_events[0].changes[0].name == "status"
    assert ticket.change_events[0].changes[0].from_value == str(
        cc.config.get()["ticket-status"]["suggest-solution"])
    assert ticket.change_events[0].changes[0].to_value == str(
        cc.config.get()["ticket-status"]["in-progress"])


def test_lazy_load_get_by_id():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)

    assert ticket is not None

    assert hasattr(ticket, "_comments") == True
    assert hasattr(ticket, "_change_events") == True
    assert hasattr(ticket, "_events") == True


def test_lazy_load():
    import clientcentral.query as operators

    ticket = cc.query_tickets().filter_by(
        operators.and_(
            operators.comparison("created_by_user.email", "=",
                                 "'thomas@labs.epiuse.com'"),
            operators.comparison("id", "=", str(pytest.ticket_id)))).all()[0]
    assert ticket is not None

    assert hasattr(ticket, "_comments") == False
    assert hasattr(ticket, "_change_events") == False
    assert hasattr(ticket, "_events") == False

    ticket.comments
    assert hasattr(ticket, "_comments") == True
    assert hasattr(ticket, "_change_events") == True
    assert hasattr(ticket, "_events") == True


def test_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.press_button("Cancel ticket", "<p>close</p>")

    assert ticket.status.status_id == cc.config.get(
    )["ticket-status"]["cancelled"]


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
#     ticket.update()
#
#     assert ticket.status == cc.config.get()["ticket-status"]["cancelled"]


@pytest.fixture(scope="module")
def close_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    print("teardown ticket")
    ticket.status = cc.config.get()["ticket-status"]["cancelled"]
    ticket.update()
