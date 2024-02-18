# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from pydantic import BaseModel, Field


class ProcessingMessage(BaseModel):
    """Message being processed

    see source for field details"""

    bovine_name: str = Field(
        examples=["vanilla_1234"],
        description="Unique identifier of the actor in the database",
    )

    submitter: str = Field(description="Actor that submitted the item")

    data: dict | list = Field(
        description="ActivityPub object being processed", examples=[{"type": "Like"}]
    )


class SendMessage(BaseModel):
    """Message being send

    see source for field details"""

    bovine_name: str = Field(
        examples=["vanilla_1234"],
        description="Unique identifier of the actor in the database",
    )

    recipient: str = Field(description="Actor the message is being send to")

    data: dict | list = Field(
        description="ActivityPub object being send", examples=[{"type": "Like"}]
    )


class FetchObjectMessage(BaseModel):
    """Request to fetch object"""

    bovine_name: str = Field(
        examples=["vanilla_1234"],
        description="Unique identifier of the actor in the database",
    )

    object_id: str = Field(description="The object to fetch")
