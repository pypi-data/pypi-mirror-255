"""helper functions for the bot."""

import logging

from typing import List
from telethon import events
from test_tele import config
from test_tele.config import Forward
from test_tele.datas.db_helper import Query

query = Query()

def admin_protect(org_func):
    """Decorate to restrict non admins from accessing the bot."""

    async def wrapper_func(event):
        """Wrap the original function."""
        admins = query.read_datas('admins', ['chat_id'])
        admins = [admin[0] for admin in admins]
        logging.info(f"Applying admin protection! Admins are {admins}")
        if event.sender_id not in admins:
            # await event.respond("You are not authorized.")
            raise events.StopPropagation
        return await org_func(event)

    return wrapper_func


def registered_user(org_func):
    """Decorate to restrict non registered user from accessing features"""

    async def wrapper_func(event):
        """Wrap the original function."""
        user = query.read_datas('users', ['is_subscriber', 'is_block'], 'chat_id = %s', [event.sender_id])
        if user:
            user = user[0]
            # Premium User
            if user[0] and not user[1]:
                return await org_func(event, True)
            elif not user[0] and not user[1]:
                return await org_func(event)
            else:
                raise events.StopPropagation
        else:
            raise events.StopPropagation

    return wrapper_func


def get_args(text: str) -> str:
    """Return the part of message following the command."""
    splitted = text.split(" ", 1)

    if not len(splitted) == 2:
        splitted = text.split("\n", 1)
        if not len(splitted) == 2:
            return ""

    prefix, args = splitted
    args = args.strip()
    logging.info(f"Got command {prefix} with args {args}")
    return args


def display_forwards(forwards: List[Forward]) -> str:
    """Return a string that beautifully displays all current forwards."""
    if len(forwards) == 0:
        return "Currently no forwards are set"
    forward_str = "This is your configuration"
    for forward in forwards:
        forward_str = (
            forward_str
            + f"\n\n```source: {forward.source}\ndest: {forward.dest}\n```\n"
        )

    return forward_str


def remove_source(source, forwards: List[Forward]) -> List[Forward]:
    """Remove a source from forwards."""
    for i, forward in enumerate(forwards):
        if forward.source == source:
            del forwards[i]
            return forwards
    raise ValueError("The source does not exist")


def get_command_prefix(val): # tambah argumen
    if config.is_bot is None:
        raise ValueError("config.is_bot is not set!")
    return "/" if val == 0 else "\." # ganti pengecekan


def get_command_suffix(val):
    if config.is_bot is None:
        raise ValueError("config.is_bot is not set!")
    return "" if val == 0 else "_me"

