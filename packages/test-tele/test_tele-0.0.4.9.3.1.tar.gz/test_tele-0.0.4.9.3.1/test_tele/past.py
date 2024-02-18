"""The module for running tgcf in past mode.

- past mode can only operate with a user account.
- past mode deals with all existing messages.
"""

import asyncio
import logging
import time
import re

from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl.custom.message import Message
from telethon.tl.patched import MessageService

from test_tele import config
from test_tele import storage as st
from test_tele.config import CONFIG, get_SESSION, write_config
from test_tele.plugins import apply_plugins
from test_tele.utils import clean_session_files, send_message


async def forward_job() -> None:
    """Forward all existing messages in the concerned chats."""
    clean_session_files()
    if CONFIG.login.user_type != 1:
        logging.warning(
            "You cannot use bot account for tgcf past mode. Telegram does not allow bots to access chat history."
        )
        return
    SESSION = get_SESSION()
    async with TelegramClient(
        SESSION, CONFIG.login.API_ID, CONFIG.login.API_HASH
    ) as client:
        config.from_to, config.reply_to = await config.load_from_to(client, config.CONFIG.forwards)
        client: TelegramClient
        for from_to, forward, reply_to in zip(config.from_to.items(), config.CONFIG.forwards, config.reply_to.items()):
            src, dest = from_to
            rpl = config.reply_to[src]
            last_id = 0
            forward: config.Forward
            logging.info(f"Forwarding messages from {src} to {dest}")
            async for message in client.iter_messages(
                src, reverse=CONFIG.past.reverse, offset_id=forward.offset
            ):
                message: Message
                event = st.DummyEvent(message.chat_id, message.id)
                event_uid = st.EventUid(event)

                if forward.end and last_id > forward.end:
                    continue
                if isinstance(message, MessageService):
                    continue
                try:
                    tm = await apply_plugins(message)
                    if not tm:
                        continue
                    st.stored[event_uid] = {}

                    if message.is_reply:
                        r_event = st.DummyEvent(
                            message.chat_id, message.reply_to_msg_id
                        )
                        r_event_uid = st.EventUid(r_event)
                    
                    for i, d in enumerate(dest):
                        if message.is_reply and r_event_uid in st.stored:
                            tm.reply_to = st.stored.get(r_event_uid).get(d)
                        if rpl and rpl[i] != 0 and not message.is_reply:
                            tm.reply_to = rpl[i]

                        fwded_msg = await send_message(d, tm)
                        if fwded_msg:
                            st.stored[event_uid].update({d: fwded_msg.id})
                    
                    tm.clear()
                    last_id = message.id
                    logging.info(f"forwarding message with id = {last_id}")
                    forward.offset = last_id
                    write_config(CONFIG, persist=False)
                    time.sleep(CONFIG.past.delay)
                    logging.info(f"slept for {CONFIG.past.delay} seconds")

                except FloodWaitError as fwe:
                    logging.info(f"Sleeping for {fwe}")
                    await asyncio.sleep(delay=fwe.seconds)
                except Exception as err:
                    logging.exception(err)
