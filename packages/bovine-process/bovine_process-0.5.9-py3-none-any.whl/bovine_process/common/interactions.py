# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging
from abc import ABC, abstractmethod

from bovine.activitystreams.utils import id_for_object
from bovine.parse import Activity
from bovine_process.types import ProcessingItem

logger = logging.getLogger(__name__)


class InteractionActor(ABC):
    """Abstract class to illustrate what is needed to process interactions"""

    @abstractmethod
    async def retrieve(self, object_id: str, only_own: bool = False) -> dict | None:
        """Retrieves an object

        :param object_id: id of the object
        :param only_own: if true requires object to be by the actor"""
        pass

    @abstractmethod
    async def remove_references(self, object_id: str) -> None:
        """Removes references to the object. Used in case an object is
        deleted and it is unknown which object it replies to"""
        pass

    @abstractmethod
    async def add_to_interaction(
        self, interaction_type: str, object_id: str, interaction: str
    ) -> None:
        """Adds to interaction

        Example object for `interaction_type = "likes"`

        ```json
        {
            "type": "Like",
            "id": interaction,
            "object": object_id
        }
        ```

        :param interaction_type: One of `likes`, `shares, `replies`
        :param object_id: id of the object being interacted with
        :param interaction: The id of the interacting object
        """
        pass

    @abstractmethod
    async def remove_from_interaction(
        self, interaction_type: str, object_id: str, interaction: str
    ) -> None:
        """Removes from interaction

        :param interaction_type: One of `likes`, `shares, `replies`
        :param object_id: id of the object being interacted with
        :param interaction: The id of the interacting object"""

        pass


async def own_object(item: ProcessingItem, actor: InteractionActor) -> dict | None:
    object_id = id_for_object(item.data.get("object"))
    if object_id is None:
        return None
    return await actor.retrieve(object_id, only_own=True)


async def like_handler(item: ProcessingItem, actor: InteractionActor) -> ProcessingItem:
    """Adds object to the likes collection of the liked object, if

    * object being liked is owner by the receiving actor"""

    obj = await own_object(item, actor)
    if obj:
        obj_id = id_for_object(obj)
        if obj_id is None:
            return item
        logger.info("Like Handler %s", obj_id)
        await actor.add_to_interaction("likes", obj_id, item.data.get("id"))

    return item


async def announce_handler(
    item: ProcessingItem, actor: InteractionActor
) -> ProcessingItem:
    """Adds object to the shares collection of the announced object, if

    * object being announced is owner by the receiving actor"""

    obj = await own_object(item, actor)
    if obj:
        obj_id = id_for_object(obj)
        if obj_id is None:
            return item
        logger.info("Announce Handler %s", obj_id)
        await actor.add_to_interaction("shares", obj_id, item.data.get("id"))

    return item


async def reply_handler(
    item: ProcessingItem, actor: InteractionActor
) -> ProcessingItem:
    """Adds object to the replies collection. Object being replied to
    is determined from `inReplyTo`. Reply is added if the object
    belongs to the receiving actor."""
    create = Activity(item.data, domain=item.submitter_domain)
    remote = await create.object_for_create(actor.retrieve)

    if not remote:
        return item

    if not remote.in_reply_to:
        return item

    obj = await actor.retrieve(remote.in_reply_to, only_own=True)

    if obj:
        obj_id = id_for_object(obj)
        if obj_id is None:
            return item
        logger.info("Reply Handler %s", obj_id)
        await actor.add_to_interaction("replies", obj_id, remote.identifier)

    return item


async def delete_reply_handler(
    item: ProcessingItem, actor: InteractionActor
) -> ProcessingItem:
    """If a reply is deleted, removes it from the replies collection"""

    remote = item.data.get("object")
    if not remote:
        return item

    if isinstance(remote, dict) and remote.get("type") == "Person":
        return item

    await actor.remove_references(remote)

    return item


async def undo_handler(item: ProcessingItem, actor: InteractionActor) -> ProcessingItem:
    """For an Undo of a Like, Dislike, Announce , they are removed from
    the appropriate collection."""

    object_to_undo = id_for_object(item.data.get("object"))
    if object_to_undo is None:
        return item

    obj = await actor.retrieve(object_to_undo)
    if obj is None:
        return item

    remote_actor = id_for_object(item.data.get("actor"))
    if obj.get("actor") != remote_actor:
        logger.error("Mismatching actor in undo from %s", remote_actor)
        return item

    obj_type = obj.get("type")
    if obj_type in ["Like", "Dislike", "http://litepub.social/ns#EmojiReact"]:
        logger.info("Undo Handler for Like of %s", obj.get("id"))
        await actor.remove_from_interaction("likes", obj.get("object"), obj.get("id"))
    elif obj_type == "Announce":
        logger.info("Undo Handler for Like of %s", obj.get("id"))
        await actor.remove_from_interaction("shares", obj.get("object"), obj.get("id"))

    return item


interaction_handlers = {
    **dict(
        Announce=announce_handler,
        Create=reply_handler,
        Delete=delete_reply_handler,
        Dislike=like_handler,
        Like=like_handler,
        Undo=undo_handler,
    ),
    "http://litepub.social/ns#EmojiReact": like_handler,
}
"""The handlers being called for interactions"""
