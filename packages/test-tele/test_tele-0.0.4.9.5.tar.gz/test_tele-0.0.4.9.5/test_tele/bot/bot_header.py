import re
from typing import TYPE_CHECKING
from telethon.tl import types

from test_tele.utils import start_sending

if TYPE_CHECKING:
    from test_tele.plugins import TgcfMessage


## Helper function for get_message
    
async def get_entity(event, entity):
    """Get chat entity from entity parameter"""
    if entity.isdigit() or entity.startswith("-"):
        chat = types.PeerChannel(int(entity))
    else:
        try:
            chat = await event.client.get_entity(entity)
        except Exception as e:
            chat = await event.client.get_entity(types.PeerChat(int(entity)))

    return chat


async def loop_message(event, chat, ids: int, next=True):
    """Loop channel posts to get message"""
    skip = 20
    tries = 0
    while True:
        if ids > 0 and tries <= skip:
            message = await event.client.get_messages(chat, ids=ids)
            tries += 1
            if not message:
                if next:
                    ids += 1
                    continue
                else:
                    ids -= 1
                    continue
            else:
                if hasattr(message, 'message'):
                    if message.media and not (message.sticker or message.voice or message.web_preview):
                        return message
                ids = ids + 1 if next else ids - 1
        else:
            return


async def ascii_image_search(file_path, url:str = None) -> list:
    """Image search using ASCII2D"""
    from PicImageSearch import Ascii2D

    url = url
    file = file_path
    bovw = False 
    proxies = None

    ascii2d = Ascii2D(
        bovw=bovw, proxies=proxies
    )
    if url:
        resp = await ascii2d.search(url=url)
    else:
        resp = await ascii2d.search(file=file)
    
    results = []
    seen_categories = set()

    for selected in (i for i in resp.raw if (i.title or i.url_list) and i.url):
        pattern = r'([-\w]+)\.[a-z]{2,3}\/'
        match = re.search(pattern, selected.url)
        if match:
            category = match.group(1).capitalize()
            if category in seen_categories:
                continue
            seen_categories.add(category)
        else:
            category = 'Unknown'

        my_dict = {
            "title": selected.title,
            "url": selected.url,
            "category": category,
            "author": selected.author,
            "author_url": selected.author_url,
        }
        results.append(my_dict)

    return results


async def ehentai_image_search(file_path, url:str = None) -> list:
    """Image search using e-hentai"""
    from PicImageSearch import EHentai, Network

    url = url
    file = file_path
    cookies = "ipb_session_id=99588dfea429026c8abb2dc5dba908a8; ipb_member_id=7096096; ipb_pass_hash=c8a343f74141f88a715eee04d96ef5eb"
    ex = False
    timeout = 60
    proxies = None

    ehentai = EHentai(proxies=proxies, cookies=cookies, timeout=timeout)
    if url:
        resp = await ehentai.search(url=url, ex=ex)
    else:
        resp = await ehentai.search(file=file, ex=ex)
    
    results = []
    seen_categories = set()

    for selected in (i for i in resp.raw if i.title and i.url):
        pattern = r'([-\w]+)\.[a-z]{2,3}\/'
        match = re.search(pattern, selected.url)
        if match:
            category = match.group(1).capitalize()
            if category in seen_categories:
                continue
            seen_categories.add(category)
        else:
            category = 'Unknown'

        my_dict = {
            "title": selected.title,
            "url": selected.url,
            "category": category
        }
        results.append(my_dict)

    return results
