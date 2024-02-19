# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import os
import aiohttp
import logging

from faststream import FastStream, Context
from faststream.annotations import ContextRepo

from bovine_store.config import tortoise_config
from tortoise import Tortoise

from bovine_propan.broker import broker

logging.basicConfig(level=logging.INFO)


app = FastStream(broker, title="BovineProcessor")
"""faststream app can be run using 

```bash
faststream run bovine_propan/__init__:app
```
"""


@app.on_startup
async def startup(context: ContextRepo):
    db_url = os.environ.get("BOVINE_DB_URL", "sqlite://bovine.sqlite3")
    await Tortoise.init(config=tortoise_config(db_url))
    await Tortoise.generate_schemas()

    session = aiohttp.ClientSession()
    context.set_global("session", session)


@app.on_shutdown
async def shutdown(session: aiohttp.ClientSession = Context()):
    await Tortoise.close_connections()
    await session.close()
