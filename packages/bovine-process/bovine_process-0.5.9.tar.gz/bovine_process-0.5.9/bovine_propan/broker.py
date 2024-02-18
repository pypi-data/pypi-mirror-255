# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
import os
import json

from faststream import Context
from faststream.annotations import Logger

from faststream.rabbit import RabbitBroker, RabbitQueue


from bovine_process.types import ProcessingItem
from bovine_process import process_inbox_item
from bovine_process.outgoing import default_async_outbox_process
from bovine_process.send_item import (
    determine_recipients,
    send_to_inbox,
    get_inbox_for_recipient,
)
from bovine.types import ServerSentEvent, Visibility
from bovine.jsonld import with_external_context

from bovine_propan.actor import bovine_actor
from bovine_propan.types import ProcessingMessage, SendMessage, FetchObjectMessage
from bovine_propan.exchanges import processing, processed

broker = RabbitBroker(os.environ.get("BOVINE_AMQP", "amqp://localhost"))

inbox_queue = RabbitQueue("inbox", auto_delete=False, routing_key="inbox")
fetch_object_queue = RabbitQueue(
    "fetch_object", auto_delete=False, routing_key="fetch_object"
)
inbox_queue_event = RabbitQueue("inbox_event", auto_delete=False, routing_key="inbox")
outbox_queue = RabbitQueue("outbox", auto_delete=False, routing_key="outbox")
to_send_queue = RabbitQueue("to_send", auto_delete=False, routing_key="to_send")


@broker.subscriber(inbox_queue, processing)
async def inbox_handler(
    message: ProcessingMessage,
    logger: Logger,
    session: aiohttp.ClientSession = Context(),
):
    """Handles events coming to the inbox"""
    async with bovine_actor(message.bovine_name, session) as actor:
        item = ProcessingItem(message.submitter, message.data)
        await process_inbox_item(item, actor)


@broker.subscriber(inbox_queue_event, processing)
async def inbox_to_event(
    message: ProcessingMessage,
    logger: Logger,
    session: aiohttp.ClientSession = Context(),
):
    """Creates a server send event for inbox events"""
    async with bovine_actor(message.bovine_name, session) as actor:
        data_s = json.dumps(message.data)
        event = ServerSentEvent(data=data_s, event="inbox")

        await broker.publish(
            event.encode(),
            routing_key=actor.actor_object.event_source,
            exchange=processed,
        )


@broker.subscriber(outbox_queue, processing)
async def outbox_handler(
    message: ProcessingMessage,
    logger: Logger,
    session: aiohttp.ClientSession = Context(),
):
    """Handles elements to the outbox"""
    async with bovine_actor(message.bovine_name, session) as actor:
        item = ProcessingItem(message.submitter, message.data)
        await default_async_outbox_process(item, actor)

        recipients = await determine_recipients(item, actor)
        to_send = with_external_context(item.data)

        for recipient in recipients:
            await broker.publish(
                SendMessage(
                    recipient=recipient,
                    data=to_send,
                    bovine_name=message.bovine_name,
                ),
                routing_key="to_send",
                exchange=processing,
            )

        data_s = json.dumps(item.data)
        event = ServerSentEvent(data=data_s, event="inbox")

        if "database_id" in item.meta:
            event.id = item.meta["database_id"]

        actor_info = actor.actor_object.build(visibility=Visibility.OWNER)
        event_source = actor_info["endpoints"]["eventSource"]

        await broker.publish(
            event.encode(), routing_key=event_source, exchange=processed
        )


@broker.subscriber(to_send_queue, processing)
async def to_send_handler(
    message: SendMessage, logger: Logger, session: aiohttp.ClientSession = Context()
):
    """Retrieves inbox for recipient and sends data"""
    async with bovine_actor(message.bovine_name, session) as actor:
        inbox = await get_inbox_for_recipient(actor, message.recipient)
        if inbox:
            await send_to_inbox(actor, inbox, message.data)


@broker.subscriber(fetch_object_queue, processed)
async def fetch_object(
    message: FetchObjectMessage,
    logger: Logger,
    session: aiohttp.ClientSession = Context(),
):
    """Meant for RPC calls. Fetches object and returns it"""
    async with bovine_actor(message.bovine_name, session) as actor:
        return await actor.retrieve(message.object_id)
