import pytest
from requests.exceptions import HTTPError

from clientcentral.clientcentral import ClientCentral

cc = ClientCentral(production=False)
pytest.ticket_id = None


def test_create_ticket():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a test ticket. Please ignore</h1>"
    sid = "ZZZ"

    ticket = cc.create_ticket(subject=subj, description=desc, sid=sid, workspace_id=cc.config.get()["ticket-workspace"]["managed-services"])

    ticket.refresh()

    assert ticket.description == desc
    assert ticket.subject == subj
    assert ticket.sid == sid
    assert ticket.owner.user_id == cc.config.get(
    )["user_ids"]["thomas-scholtz"]
    assert ticket.status.status_id == cc.config.get()["ticket-status"]["new"]
    assert ticket.status.name == "New"
    assert ticket.priority == cc.config.get()["ticket-priority"]["very-low"]

    pytest.ticket_id = ticket.ticket_id


def test_comment():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    old_num_comments = len(ticket.comments)
    old_num_change_eventes = len(ticket.change_events)

    ticket.comment("<p>Test desc</p>")
    new_num_comments = len(ticket.comments)
    new_num_change_events = len(ticket.change_events)

    assert (old_num_comments + 1) == new_num_comments
    assert ticket.comments[0].comment == "<p>Test desc</p>"

    # nothing else should have changed unless someone edited the ticket.
    assert (old_num_change_eventes + 1) == new_num_change_events


def test_grab():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.grab()
    assert ticket.assignee == cc.config.get()["user_ids"]["thomas-scholtz"]
    assert ticket.status.status_id == cc.config.get(
    )["ticket-status"]["in-progress"]
    assert ticket.status.name == "In progress"


def test_suggest_solution():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.suggest_solution("<p>sol</p>")


def test_comment_and_update():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.description = "<p>update desc</p>"
    ticket.comment_and_update("comment and update")


def test_suggest_solution_then_grab():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    with pytest.raises(HTTPError):
        ticket.suggest_solution("sol")
    with pytest.raises(HTTPError):
        ticket.grab()


def test_decline_solution():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.decline("<p>decline</p>")

    assert ticket.status.status_id == cc.config.get(
    )["ticket-status"]["in-progress"]


def test_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.cancel_ticket("<p>close</p>")

    assert ticket.status.status_id == cc.config.get(
    )["ticket-status"]["cancelled"]


@pytest.fixture(scope="module")
def close_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    print("teardown ticket")
    ticket.status = cc.config.get()["ticket-status"]["cancelled"]
    ticket.update()
