# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging

from typing import Callable, Awaitable

from bovine.jsonld import with_bovine_context

from bovine_process.utils import ByActivityType
from bovine_process.types import ProcessingItem

from .interactions import interaction_handlers, InteractionActor

logger = logging.getLogger(__name__)


interaction_processor: Callable[
    [ProcessingItem, InteractionActor], Awaitable[ProcessingItem]
] = ByActivityType(**interaction_handlers)
"""Defines the processor that handles interactions with an object"""


async def sanitize(item: ProcessingItem, actor):
    """Applies the default bovine context"""
    item.data = with_bovine_context(item.data)

    if item.submitter != item.data.get("actor"):
        logger.error("Got wrong submitter for an activity %s", item.submitter)
        logger.error(item.data)
        # return

    return item
