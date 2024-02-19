"""Utility functions to smoothen your life."""

import os
import re
import sys
import logging
import platform
from datetime import datetime
from typing import TYPE_CHECKING

from telethon.client import TelegramClient
from telethon.hints import EntityLike
from telethon.tl.functions.messages import TranslateTextRequest
from telethon.tl.types.messages import TranslateResult
from telethon.tl.custom.message import Message

from test_tele import __version__
from test_tele import storage as st
from test_tele.config import CONFIG
from test_tele.plugin_models import STYLE_CODES, SendAs

if TYPE_CHECKING:
    from test_tele.plugins import TgcfMessage

ALBUM_ID = None
CAPTION = []
MEDIA_ALBUM = []

def platform_info():
    nl = "\n"#Running tgcf {__version__}\
    return f""" 
    Python {sys.version.replace(nl,"")}\
    \nOS {os.name}\
    \nPlatform {platform.system()} {platform.release()}\
    \n{platform.architecture()} {platform.processor()}"""


async def send_message(recipient: EntityLike, tm: "TgcfMessage") -> Message:
    """Forward or send a copy, depending on config."""
    client: TelegramClient = tm.message.client

    if CONFIG.show_forwarded_from:
        as_album = None
        if CONFIG.plugins.special.check and CONFIG.plugins.special.send_as == SendAs.ALBUM:
            as_album = True
        return await client.forward_messages(
            recipient, tm.message, silent=True, as_album=as_album, background=True
        )
        
    if CONFIG.plugins.special.check and CONFIG.plugins.special.send_as != SendAs.ONEBYONE:
        if CONFIG.mode == 1: # past
            if CONFIG.plugins.special.send_as == SendAs.SOURCE:
                return await get_album(recipient, tm)
        elif CONFIG.mode == 0: # live
            if CONFIG.plugins.special.send_as == SendAs.SOURCE:
                return await start_sending(recipient, tm)
        else:
            return await start_sending(recipient, tm)
    else:
        return await start_sending(recipient, tm)


async def start_sending(recipient: EntityLike, tm: "TgcfMessage") -> Message:
    """Handle sending message with either send_file or send_message"""
    client = tm.message.client

    async with client.action(recipient, 'typing'):
        if tm.new_file:
            try:
                message = await client.send_file(
                    recipient, tm.new_file, caption=tm.text, 
                    reply_to=tm.reply_to, silent=True, background=True, 
                    force_document=False
                )
                return message
            except Exception as err:
                logging.warning(f"Cannot send as album, sending one by one instead : {err}")
                for item in tm.new_file:
                    try:
                        await client.send_file(
                            recipient, item, caption=tm.text, 
                            reply_to=tm.reply_to, silent=True, background=True, 
                            force_document=False
                        )
                    except Exception as er:
                        logging.error(er)
                        pass
                return
        else:
            tm.message.text = tm.text
            return await client.send_message(
                recipient, tm.message, reply_to=tm.reply_to, silent=True, background=True
            )


# Work well in past mode
async def send_message_source(recipient: EntityLike, tm: "TgcfMessage") -> Message:
    """Send messages similar to the source"""
    client = tm.message.client
    global MEDIA_ALBUM
    caption = None

    if MEDIA_ALBUM:
        if CAPTION and (CAPTION[-1] != '' or CAPTION[0] != '') and CONFIG.mode == 1 and CONFIG.past.reverse:
            caption = CAPTION[0]
        else:
            caption = CAPTION[-1]
        return await client.send_file(
            recipient, MEDIA_ALBUM, caption=caption, reply_to=tm.reply_to
        )
    else:
        return await start_sending(recipient, tm)


async def get_album(recipient: EntityLike, tm: "TgcfMessage") -> Message:
    global MEDIA_ALBUM, ALBUM_ID, CAPTION

    if tm.message.grouped_id != None:
        if tm.message.grouped_id != ALBUM_ID and MEDIA_ALBUM:
            await send_message_source(recipient, tm)
            MEDIA_ALBUM = []
            CAPTION = []
            ALBUM_ID = tm.message.grouped_id
            MEDIA_ALBUM.append(tm.message.media)
            CAPTION.append(tm.text)
            return
        else:
            ALBUM_ID = tm.message.grouped_id
            MEDIA_ALBUM.append(tm.message.media)
            CAPTION.append(tm.text)
    elif tm.message.grouped_id != ALBUM_ID:
        message = await send_message_source(recipient, tm)
        MEDIA_ALBUM = []
        CAPTION = []
        ALBUM_ID = tm.message.grouped_id
        if tm.message.grouped_id != None:
            MEDIA_ALBUM.append(tm.message.media)
            CAPTION.append(tm.text)
        else:
            message = await send_message_source(recipient, tm)
            return message
    else:
        if MEDIA_ALBUM:
            message = await send_message_source(recipient, tm)
            MEDIA_ALBUM = []
            CAPTION = []
        message = await send_message_source(recipient, tm)
        return message


async def upload_files(tm: "TgcfMessage", media_list, folder_path, file_name):
    client = tm.message.client

    file_path = os.path.join(folder_path, file_name)
    
    with open(file_path, 'rb') as file:
        media_photo = await client.upload_file(file=file, part_size_kb=512, file_name=file_name)
        media_list.append(media_photo)
    cleanup(file_path)

    return media_list


async def translate(tm: "TgcfMessage") -> Message:
    """Live translate the message text."""
    client = tm.message.client
    if tm.text:
        try:
            translate_text_result: TranslateResult = await client(TranslateTextRequest(
                to_lang=CONFIG.plugins.special.lang,
                peer=tm.message.chat_id,
                id=tm.message.id,
                text=tm.text
            ))
            tm.text = translate_text_result.text
            tm.text += tm.links
        except Exception as e:
            logging.error(f"{e}")
            pass
    return tm


def cleanup(*files: str) -> None:
    """Delete the file names passed as args."""
    for file in files:
        try:
            os.remove(file)
        except FileNotFoundError:
            logging.info(f"File {file} does not exist, so cant delete it.")


def stamp(file: str, user: str) -> str:
    """Stamp the filename with the datetime, and user info."""
    now = str(datetime.now())
    outf = safe_name(f"{user} {now} {file}")
    try:
        os.rename(file, outf)
        return outf
    except Exception as err:
        logging.warning(f"Stamping file name failed for {file} to {outf}. \n {err}")


def safe_name(string: str) -> str:
    """Return safe file name.

    Certain characters in the file name can cause potential problems in rare scenarios.
    """
    return re.sub(pattern=r"[-!@#$%^&*()\s]", repl="_", string=string)


def match(pattern: str, string: str, regex: bool) -> bool:
    if regex:
        return bool(re.findall(pattern, string))
    return pattern in string


def replace(pattern: str, new: str, string: str, regex: bool) -> str:
    def fmt_repl(matched):
        style = new
        s = STYLE_CODES.get(style)
        return f"{s}{matched.group(0)}{s}"

    if regex:
        if new in STYLE_CODES:
            compliled_pattern = re.compile(pattern)
            return compliled_pattern.sub(repl=fmt_repl, string=string)
        return re.sub(pattern, new, string)
    else:
        return string.replace(pattern, new)


def clean_session_files():
    for item in os.listdir():
        if item.endswith(".session") or item.endswith(".session-journal"):
            os.remove(item)
