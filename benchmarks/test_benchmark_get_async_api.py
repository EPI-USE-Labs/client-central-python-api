import pytest

import asyncio

from clientcentral.clientcentral import ClientCentral
from clientcentral.model.Status import Status
from clientcentral.Exceptions import (
    ButtonNotAvailable,
    ButtonRequiresComment,
    HTTPError,
)


def _get_event_loop():
    """Retrieves the event loop or creates a new one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def benchmark_async_get_tickets():
    async_cc = ClientCentral(production=False, run_async=True)
    to_fetch_list = []

    for x in range(86060, 86090):
        to_fetch_list.append(async_cc.get_ticket_by_id(x))

    future = asyncio.ensure_future(asyncio.gather(*to_fetch_list))
    result = _get_event_loop().run_until_complete(future)


def benchmark_get_tickets():
    cc = ClientCentral(production=False, run_async=False)
    for x in range(86060, 86090):
        cc.get_ticket_by_id(x)


def test_get_multiple_tickets_async(benchmark):
    benchmark(benchmark_async_get_tickets)


def test_get_multiple_tickets(benchmark):
    benchmark(benchmark_get_tickets)
