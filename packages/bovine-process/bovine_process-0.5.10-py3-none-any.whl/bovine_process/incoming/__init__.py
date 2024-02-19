# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from bovine_process.utils import ProcessorList, ByActivityType
from bovine_process.common import interaction_processor, sanitize

from .following import accept_follow, undo_follow
from .handle_update import handle_update
from .incoming_delete import incoming_delete
from .store_incoming import add_incoming_to_inbox, store_incoming


crud_handlers = dict(Update=handle_update, Delete=incoming_delete)
"""The handlers being called for CRUD operations"""

social_handlers = dict(Accept=accept_follow, Undo=undo_follow)
"""The handlers being called for social interactions, i.e. updating the social graph"""


default_inbox_process = ProcessorList(
    sanitize,
    store_incoming,
    ByActivityType(**crud_handlers),
    ByActivityType(**social_handlers),
    interaction_processor,
    add_incoming_to_inbox,
)
"""Represents the default process undertaken by an inbox item"""
