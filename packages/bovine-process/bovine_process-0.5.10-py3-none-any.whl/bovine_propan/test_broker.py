# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
import pytest

from faststream.rabbit import TestRabbitBroker
from faststream.annotations import ContextRepo
from unittest.mock import AsyncMock, MagicMock

from .actor import cache

from .broker import broker, inbox_queue, fetch_object_queue
from bovine_propan.exchanges import processing, processed


@pytest.fixture
async def test_broker():
    async with TestRabbitBroker(broker) as br:
        context = ContextRepo()
        context.set_global("session", AsyncMock(aiohttp.ClientSession))
        context.set_global("logger", AsyncMock())

        actor = AsyncMock()
        actor.actor_id = "http://local/actor"
        cache["bovine_name"] = actor
        actor.actor_object.build = MagicMock(
            return_value={"endpoints": {"eventSource": "xxxx"}}
        )
        actor.retrieve_own_object.return_value = MagicMock()
        actor.retrieve.return_value = {"some": "object"}

        yield br


async def test_inbox_handler(test_broker):
    remote_actor = "https://remote.example/actor"

    await test_broker.publish(
        {
            "bovine_name": "bovine_name",
            "submitter": remote_actor,
            "data": {
                "@context": "about:bovine",
                "actor": remote_actor,
                "type": "Like",
            },
        },
        exchange=processing,
        queue=inbox_queue,
    )


async def test_fetch_object(test_broker):
    result = await test_broker.publish(
        {"bovine_name": "bovine_name", "object_id": "http://object.example"},
        exchange=processed,
        queue=fetch_object_queue,
        rpc=True,
    )

    assert result == {"some": "object"}
