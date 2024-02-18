import re
import logging

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.handlers import (MessageHandler, EditedMessageHandler)
from pyrogram.enums import ParseMode
from pyrogram.enums import MessageEntityType

from test_tele.datas import db_helper as dbh


query = dbh.Query()


async def find_links(text):
    link_pattern = r'((?:t.me/|@)[_0-9a-zA-Z/]+)'

    links = []
    for link in re.findall(link_pattern, text):
        link_type = 'sticker' if 'addstickers' in link else 'addlist' if 'addlist' in link else 'channel'
        links.append((link, link_type))
    return links


async def save_links(links):
    for link, link_type in links:
        link: str = link.replace("@", "t.me/")
        if link_type == 'channel':
            if link.endswith("bot") or link.endswith("Bot"):
                continue
            tme, url, *id = link.split("/")
            link = f"{tme}/{url}"
        link = "https://" + link
        if not query.read_datas('links', None, 'url = %s', [link]):
            query.create_data('links', ['url', 'type'], [link, link_type])


async def get_links(event):
    links = await find_links(event.text)
    if links:
        await save_links(links)

    try:
        for entity in event.entities:
            if entity.type == MessageEntityType.TEXT_LINK:
                links = await find_links(entity.url)
                await save_links(links)
    except:
        pass


async def incoming_message_handler(app, message: Message):
    """Handle spesific incoming message"""
    try:
        if message.text:
            # grab links
            await get_links(message)
        # elif message.photo:
            # logging.warning("ya ini photo")
            # logging.warning(message.photo)
        elif message.sticker:
            # logging.warning("ya ini sticker")
            link = await find_links(f"t.me/addstickers/{message.sticker.set_name}")
            await save_links(link)
            
    except Exception as err:
        logging.error(err, exc_info=True)
    

async def edited_message_handler(app, message: Message):
    """Handle spesific edited message"""
    try:
        if message.text:
            await get_links(message)
            
    except Exception as err:
        logging.error(err, exc_info=True)


# For user & bot but mostly for user
PYROGRAM_HANDLERS = {
    "in_message": MessageHandler(incoming_message_handler, filters.text | filters.photo | filters.sticker),
    "update_message": EditedMessageHandler(edited_message_handler, filters.text)
}
