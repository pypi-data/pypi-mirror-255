# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from bovine_process.utils import ProcessorList, ByActivityType

from bovine_process.common import interaction_processor, sanitize

from .following import accept_follow, undo_follow
from .outgoing_delete import outgoing_delete
from .outgoing_update import outgoing_update
from .store_outgoing import add_outgoing_to_outbox, store_outgoing
from .update_id import update_id

default_outbox_process = ProcessorList(
    sanitize,
    update_id,
    store_outgoing,
    add_outgoing_to_outbox,
    ByActivityType(
        Update=outgoing_update,
        Delete=outgoing_delete,
    ),
)
"""Defines the synchronous part of sending an outgoing object"""


social_processor = ByActivityType(Accept=accept_follow, Undo=undo_follow)
"""Processes outgoing social events, i.e. updates the social graph"""


default_async_outbox_process = ProcessorList(social_processor, interaction_processor)
"""Defines the asynchronous part of handling an outgoing object"""
