# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging
import aiohttp

from bovine_store import BovineStore
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

cache = {}


@asynccontextmanager
async def bovine_actor(bovine_name: str, session: aiohttp.ClientSession):
    """Yields the BovineStoreActor corresponding to the `bovine_name`.
    Usage:

    ```python
    async with bovine_actor(bovine_name, session) as actor:
        ...
    ```
    """
    if bovine_name not in cache:
        store = BovineStore(session=session)
        actor = await store.actor_for_name(bovine_name)
        cache[bovine_name] = actor

    try:
        yield cache[bovine_name]
    except Exception as e:
        logger.exception(e)
