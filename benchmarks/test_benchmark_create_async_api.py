import pytest

import asyncio

from clientcentral.clientcentral import ClientCentral
from clientcentral.model.Status import Status
from clientcentral.Exceptions import (
    ButtonNotAvailable,
    ButtonRequiresComment,
    HTTPError,
)

async_cc = ClientCentral(production=False, run_async=True)
cc = ClientCentral(production=False, run_async=False)

pytest.ticket_id = None

pytest.ticket_id_related = None


def _get_event_loop():
    """Retrieves the event loop or creates a new one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def benchmark_create_multiple_tickets_async():
    to_create_list = []

    for x in range(0, 10):
        to_create_list.append(
            async_cc.create_ticket(
                subject="[ASYNC Test ticket]",
                description="Test ticket",
                project_id=8,
                workspace_id=141,
                # assignee="User:14012",
                priority=33,
                custom_fields_attributes=[
                    {"id": 17, "values": 0},
                    {"id": 75, "values": 363},
                ],
            )
        )

    future = asyncio.ensure_future(asyncio.gather(*to_create_list))
    result = _get_event_loop().run_until_complete(future)


def benchmark_create_multiple_tickets():
    for x in range(0, 10):
        cc.create_ticket(
            subject="[SERIAL Test ticket]",
            description="Test ticket",
            project_id=8,
            workspace_id=141,
            # assignee="User:14012",
            priority=33,
            custom_fields_attributes=[
                {"id": 17, "values": 0},
                {"id": 75, "values": 363},
            ],
        )


def test_create_multiple_tickets_async(benchmark):
    benchmark(benchmark_create_multiple_tickets_async)


def test_create_multiple_tickets(benchmark):
    benchmark(benchmark_create_multiple_tickets)
