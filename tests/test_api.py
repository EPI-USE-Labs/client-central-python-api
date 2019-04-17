import pytest
from requests.exceptions import HTTPError

from clientcentral.clientcentral import ClientCentral

cc = ClientCentral(production=False)
pytest.ticket_id = None


def test_create_ticket():
    subj = "[Test-Ticket]"
    desc = "<p>This is a test ticket. Please ignore</p>"
    sid = "ZZZ"

    ticket = cc.create_ticket(subject=subj, description=desc, sid=sid)

    ticket.refresh()

    assert ticket.description == desc
    assert ticket.subject == subj
    assert ticket.sid == sid
    assert ticket.owner == cc.config.get()["user_ids"]["thomas-scholtz"]
    assert ticket.status == cc.config.get()["ticket-status"]["new"]
    assert ticket.priority == cc.config.get()["ticket-priority"]["very-low"]

    pytest.ticket_id = ticket.ticket_id


def test_comment():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.comment("<p>Test desc</p>")

def test_grab():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.grab()
    assert ticket.assignee == cc.config.get()["user_ids"]["thomas-scholtz"]
    assert ticket.status == cc.config.get()["ticket-status"]["in-progress"]


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

    assert ticket.status == cc.config.get()["ticket-status"]["in-progress"]


def test_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    ticket.cancel_ticket("<p>close</p>")

    assert ticket.status == cc.config.get()["ticket-status"]["cancelled"]


@pytest.fixture(scope="module")
def close_cancel():
    ticket = cc.get_ticket_by_id(pytest.ticket_id)
    print("teardown ticket")
    ticket.status = cc.config.get()["ticket-status"]["cancelled"]
    ticket.update()
