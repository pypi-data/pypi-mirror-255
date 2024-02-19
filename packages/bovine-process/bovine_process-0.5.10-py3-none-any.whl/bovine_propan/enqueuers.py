# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import os

from faststream.rabbit import RabbitBroker
from bovine_process.types import ProcessingItem

from .exchanges import processing
from .types import ProcessingMessage

amqp_uri = os.environ.get("BOVINE_AMQP", "amqp://localhost")

enqueue_broker = RabbitBroker(amqp_uri)
"""Broker to be used for enqueuing items. amqp uri is determined from BOVINE_AMQP
environment variable. Otherwise `amqp://localhost`"""


async def enqueue_to_inbox(item: ProcessingItem, actor):
    """Enqueues a message for inbox processing"""
    await enqueue_broker.publish(
        ProcessingMessage(
            bovine_name=actor.bovine_name, data=item.data, submitter=item.submitter
        ),
        exchange=processing,
        routing_key="inbox",
    )


async def enqueue_to_outbox(item: ProcessingItem, actor):
    """Enqueues a message for outbox processing"""
    await enqueue_broker.publish(
        ProcessingMessage(
            bovine_name=actor.bovine_name, data=item.data, submitter=item.submitter
        ),
        exchange=processing,
        routing_key="outbox",
    )
