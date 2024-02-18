"""The module responsible for operating tgcf in live mode via Telethon"""

import re
import sys
import logging
from typing import Union

from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
from telethon.tl.custom.message import Message
from telethon.tl.types import MessageEntityTextUrl

from test_tele import config, const
from test_tele import storage as st
from test_tele.bot import get_events, get_handlers
from test_tele.config import CONFIG, get_SESSION
from test_tele.plugins import apply_plugins
from test_tele.utils import clean_session_files, send_message


async def new_message_handler(event: Union[Message, events.NewMessage]) -> None:
    """Process new incoming messages."""
    chat_id = event.chat_id

    if chat_id not in config.from_to:
        return

    logging.info(f"New message received in {chat_id}")
    message = event.message

    event_uid = st.EventUid(event)

    length = len(st.stored)
    exceeding = length - const.KEEP_LAST_MANY

    if exceeding > 0:
        for key in st.stored:
            del st.stored[key]
            break

    dest = config.from_to.get(chat_id)
    rpl = config.reply_to[chat_id]

    tm = await apply_plugins(message)
    if not tm:
        return

    if event.is_reply:
        r_event = st.DummyEvent(chat_id, event.reply_to_msg_id)
        r_event_uid = st.EventUid(r_event)
        
    st.stored[event_uid] = {}
    for i, d in enumerate(dest):
        if event.is_reply and r_event_uid in st.stored:
            tm.reply_to = st.stored.get(r_event_uid).get(d)
        if rpl and rpl[i] != 0 and not event.is_reply:
            tm.reply_to = rpl[i]
        fwded_msg = await send_message(d, tm)
        st.stored[event_uid].update({d: fwded_msg})

    tm.clear()


async def edited_message_handler(event) -> None:
    """Handle message edits."""
    message = event.message
    chat_id = event.chat_id

    if chat_id not in config.from_to:
        return

    logging.info(f"Message edited in {chat_id}")

    event_uid = st.EventUid(event)
    tm = await apply_plugins(message)

    if not tm:
        return

    fwded_msgs = st.stored.get(event_uid)

    if fwded_msgs:
        for _, msg in fwded_msgs.items():
            if config.CONFIG.live.delete_on_edit == message.text:
                await msg.delete()
                await message.delete()
            else:
                await msg.edit(tm.text)
        return

    dest = config.from_to.get(chat_id)
    rpl = config.reply_to[chat_id]

    for i, d in enumerate(dest):
        if rpl and rpl[i] != 0:
            tm.reply_to = rpl[i]
        await send_message(d, tm)

    tm.clear()


async def deleted_message_handler(event):
    """Handle message deletes."""
    chat_id = event.chat_id
    if chat_id not in config.from_to:
        return

    logging.info(f"Message deleted in {chat_id}")

    event_uid = st.EventUid(event)
    fwded_msgs = st.stored.get(event_uid)
    if fwded_msgs:
        for _, msg in fwded_msgs.items():
            await msg.delete()
        return


USER_BOT_HANDLER = {
    "new": (new_message_handler, events.NewMessage()),
    "edited": (edited_message_handler, events.MessageEdited()),
    "deleted": (deleted_message_handler, events.MessageDeleted()),
}
