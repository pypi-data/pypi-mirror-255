# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging

logger = logging.getLogger(__name__)


async def do_nothing(item, *args):
    return item


class ByActivityType:
    """Simplifies handling activity by type, usage:

    ```python
    by_type = ByActivityType(One=do_one, Two=do_two})

    by_type({"type": one}, arg1, arg2) # calls do_one({"type": one}, arg1, arg2)
    ```
    """

    def __init__(self, **kwargs):
        self.actions = kwargs

    async def __call__(self, item, *args):
        try:
            item_type = item.data.get("type")
            if item_type is None:
                return item
            if isinstance(item_type, str):
                if item_type in self.actions:
                    return await self.actions[item_type](item, *args)
                else:
                    return item
            elif isinstance(item_type, list):
                for single_type in item_type:
                    item = await self.actions[single_type](item, *args)
                return item
            else:
                return item

        except Exception as ex:
            logger.error("Something went wrong with %s during procession", repr(ex))
            logger.exception(ex)
            if item:
                logger.error(item.data)


class ProcessorList:
    """Creates a list of processors, usage:

    ```python
    processors = ProcessorList(my_processor,
        ByActivityType(Follow=my_follow_processor))
    await processors(item, args)
    ```"""

    def __init__(self, *processors):
        self.processors = list(processors)

    async def __call__(self, item, *arguments):
        working = item

        try:
            for processor in self.processors:
                working = await processor(working, *arguments)
                if not working:
                    return

            return working
        except Exception as ex:
            logger.exception(ex)
            raise ex
