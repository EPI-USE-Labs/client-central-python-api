import pytest

import asyncio

from clientcentral.clientcentral import ClientCentral
from clientcentral.model.Status import Status
from clientcentral.model.TicketType import TicketType
from clientcentral.Exceptions import (
    ButtonNotAvailable,
    ButtonRequiresComment,
    HTTPError,
)

pytest.ticket_id = None

async_cc = ClientCentral(production=False, run_async=True)


def _get_event_loop():
    """Retrieves the event loop or creates a new one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


async def create_ticket():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a test ticket. Please ignore</h1>"

    ticket = await async_cc.create_ticket(
        account_vp=1,
        customer_user_vp=1,
        subject=subj,
        description=desc,
        project_id=8,
        workspace_id=141,
        # assignee="User:14012",
        priority=33,
        type_id=8,
        custom_fields_attributes=[{"id": 17, "values": 0}, {"id": 75, "values": 363}],
    )

    assert ticket.run_async == True
    assert ticket._net_calls == 3
    assert ticket.subject == subj
    assert ticket.description == "<h1>This is a test ticket. Please ignore</h1>"
    assert ticket.project_id == 8
    assert ticket.priority == 33
    assert ticket.workspace_id == 141
    assert ticket.internal == False

    assert (await ticket.custom_fields)["ms_category"]["name"] == "Other"
    assert ticket._net_calls == 3

    assert hasattr(ticket, "_custom_fields_attribute") == True
    assert (await ticket.custom_fields)["ms_category"]["id"] == 363
    assert ticket._net_calls == 3

    pytest.ticket_id = ticket.ticket_id


def test_create_ticket():
    loop = async_cc._event_loop
    future = loop.create_task(create_ticket())
    loop.run_until_complete(future)


async def get_ticket_by_id():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a test ticket. Please ignore</h1>"
    ticket = await async_cc.get_ticket_by_id(pytest.ticket_id)
    assert ticket._net_calls == 2
    assert ticket.run_async == True
    assert ticket.subject == subj
    assert ticket.description == "<h1>This is a test ticket. Please ignore</h1>"
    assert ticket.project_id == 8
    assert ticket.priority == 33
    assert ticket.workspace_id == 141
    assert ticket.internal == False

    assert (await ticket.custom_fields)["ms_category"]["name"] == "Other"
    assert ticket._net_calls == 2

    assert hasattr(ticket, "_custom_fields_attribute") == True
    assert (await ticket.custom_fields)["ms_category"]["id"] == 363
    assert ticket._net_calls == 2

    assert len((await ticket.comments)) == 0
    assert ticket._net_calls == 2


def test_get_ticket_by_id():
    loop = async_cc._event_loop
    future = loop.create_task(get_ticket_by_id())
    loop.run_until_complete(future)


async def update_ticket():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a test ticket. Please ignore</h1>"
    ticket = await async_cc.get_ticket_by_id(pytest.ticket_id)
    assert ticket._net_calls == 2
    assert ticket.run_async == True
    assert ticket.subject == subj
    assert ticket.description == "<h1>This is a test ticket. Please ignore</h1>"
    assert ticket.project_id == 8
    assert ticket.priority == 33
    assert ticket.workspace_id == 141
    assert ticket.internal == False
    assert ticket.type.type_id == 8
    assert ticket.type.name == "Incident"

    ticket.subject = "UPDATED SUBJECT"
    ticket.description = "UPDATED DESCRIPTION"
    ticket.priority = 2
    ticket.type = TicketType(9)
    ticket.assignee = "User:14012"
    ticket.custom_fields_attributes = [
        {"id": 17, "values": 1},
        {"id": 75, "values": 360},
    ]

    await ticket.commit()
    assert ticket._net_calls == 5  # Should be 4 as we dont need to update the buttons

    assert ticket.subject == "UPDATED SUBJECT"
    assert ticket.description == "UPDATED DESCRIPTION"
    assert ticket.internal == False  # This workspace does not have a customer
    assert ticket.priority == 2
    assert ticket.assignee == "User:14012"
    assert ticket.type.type_id == 9
    assert ticket.type.name == "Service request"
    assert (await ticket.custom_fields)["ms_category"]["name"] == "Transports"


def test_update_ticket_by_id():
    loop = async_cc._event_loop
    future = loop.create_task(update_ticket())
    loop.run_until_complete(future)


async def move_ticket_to_workspace():
    subj = "[Test-Ticket]"
    desc = "<h1>This is a test ticket. Please ignore</h1>"

    ticket = await async_cc.create_ticket(
        account_vp=1,
        customer_user_vp=1,
        subject=subj,
        description=desc,
        project_id=8,
        workspace_id=25,
        # assignee="User:14012",
        priority=33,
        type_id=8,
        custom_fields_attributes=[{"id": 17, "values": 0}, {"id": 75, "values": 363}],
    )

    assert ticket.run_async == True
    assert ticket._net_calls == 3
    assert ticket.subject == subj
    assert ticket.description == "<h1>This is a test ticket. Please ignore</h1>"
    assert ticket.project_id == 8
    assert ticket.priority == 33
    assert ticket.workspace_id == 25
    assert ticket.internal == False

    ticket.subject = "UPDATED SUBJECT"
    ticket.description = "UPDATED DESCRIPTION"
    ticket.priority = 2
    ticket.workspace_id = 87
    ticket.project_id = 175
    ticket.type = TicketType(9)
    ticket.assignee = "User:14012"
    ticket.internal = True
    ticket.custom_fields_attributes = [
        {"id": 17, "values": 1},
        {"id": 75, "values": 360},
    ]

    await ticket.commit()

    assert ticket.subject == "UPDATED SUBJECT"
    assert ticket.description == "UPDATED DESCRIPTION"
    assert ticket.internal == True
    assert ticket.priority == 2
    assert ticket.workspace_id == 87
    assert ticket.assignee == "User:14012"
    assert ticket.type.type_id == 9
    assert ticket.type.name == "Service request"
    assert (await ticket.custom_fields)["ms_category"]["name"] == "Other"


def test_move_ticket_to_workspace():
    loop = async_cc._event_loop
    future = loop.create_task(move_ticket_to_workspace())
    loop.run_until_complete(future)


def test_get_user_by_email():
    users_client = async_cc.get_users_client()
    user = users_client.get_user_by_email("thomas@labs.epiuse.com")

    assert user.email == "thomas@labs.epiuse.com"
    assert user.first_name == "Thomas"
    assert user.last_name == "Scholtz"
