# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from unittest.mock import AsyncMock

from . import ProcessorList


async def test_processor_list():
    mock1 = AsyncMock()
    mock2 = AsyncMock()
    mock1.return_value = None

    processor_list = ProcessorList(mock1, mock2)

    item = "item"

    result = await processor_list(item)

    mock1.assert_awaited_once()
    mock2.assert_not_awaited()

    assert result is None
