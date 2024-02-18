# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import pytest
from faststream.rabbit import TestRabbitBroker
from unittest.mock import MagicMock

from bovine_process.types import ProcessingItem

from .enqueuers import enqueue_to_inbox, enqueue_broker


@pytest.fixture
async def test_broker():
    async with TestRabbitBroker(enqueue_broker) as broker:
        yield broker


async def test_enqueue_inbox(test_broker):
    item = ProcessingItem("submitter", {})
    await enqueue_to_inbox(item, MagicMock(bovine_name="bovine_name"))
