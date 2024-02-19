# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from unittest.mock import AsyncMock

from bovine_process.types import ProcessingItem

from . import ByActivityType, do_nothing


async def test_do_nothing():
    item = ProcessingItem("submitter", "item")

    assert await do_nothing(item, "other arg") == item
    assert await do_nothing(item, "other arg", {"more": "arguments"}) == item


async def test_by_activity_type():
    item = ProcessingItem("submitter", {"type": "Test"})

    mock = AsyncMock()
    mock.return_value = "mock"

    by_activity_type = ByActivityType(Test=mock)

    result = await by_activity_type(item)

    assert result == "mock"
    mock.assert_awaited_once()


async def test_build_do_for_types():
    follow_item = ProcessingItem("submitter", {"type": "Follow"})
    create_item = ProcessingItem("submitter", {"type": "Create"})
    blank_item = ProcessingItem("submitter", {})

    mock = AsyncMock()
    mock.return_value = "mock"

    processor = ByActivityType(Follow=mock)

    assert await processor(follow_item) == "mock"
    assert await processor(create_item) == create_item
    assert await processor(blank_item) == blank_item

    mock.assert_awaited_once()


async def test_allow_for_types_being_a_list():
    funny_item = ProcessingItem("submitter", {"type": ["One", "Two"]})

    mock_one = AsyncMock()
    mock_two = AsyncMock()

    await ByActivityType(One=mock_one, Two=mock_two)(funny_item)

    mock_one.assert_awaited_once()
    mock_two.assert_awaited_once()
