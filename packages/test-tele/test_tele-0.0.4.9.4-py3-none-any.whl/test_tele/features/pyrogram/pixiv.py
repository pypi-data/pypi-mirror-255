import uuid 
import logging

from test_tele.features.extractors.pixiv import *
from test_tele.features.pyrogram.utils import not_found_msg, get_user_setting
from pyrogram.types import (InlineQueryResultArticle, InlineQueryResultPhoto, InlineQueryResultVideo, InlineKeyboardMarkup, 
                            InlineKeyboardButton, InputTextMessageContent, InlineQueryResultAnimation)


async def image_keyboard(query: str, my_list: list[str]) -> InlineKeyboardMarkup:
    url = my_list['img_urls']['img_original'].split("/img/")[-1]
    buttons = [[
                InlineKeyboardButton("👤🔄",
                                     switch_inline_query_current_chat=f".px id:{my_list['user_id']}"),
                InlineKeyboardButton("🔗🔄",
                                     switch_inline_query_current_chat=f".px {my_list['id']}")
            ],[
                InlineKeyboardButton("💾" ,
                                     callback_data=f"px {url}"),
                InlineKeyboardButton("🔄",
                                     switch_inline_query_current_chat=query),
            ]]
    return InlineKeyboardMarkup(buttons)


async def inline_query_result(my_list, query, px_mode):
    caption = (
        f"**[{my_list['title']}](https://www.pixiv.net/en/artworks/{my_list['id']})**\n"
        f"Artist : [{my_list['user_name']}](https://www.pixiv.net/en/users/{my_list['user_id']})\n"
        f"Tags : {my_list['tags']}"
    )

    sample_img = my_list['img_urls']['img_sample'].replace('540x540_70', '600x1200_90')
    thumb_img = my_list['img_urls']['img_thumb'].replace('540x540_70', '400x250_80')

    if str(my_list['img_urls']['img_sample']).endswith(tuple(IMG_EXT)):
        result = InlineQueryResultPhoto(
            photo_url=sample_img,
            thumb_url=thumb_img,
            id=str(uuid.uuid4()) + my_list['id'],
            caption=caption if 'no_tag' not in px_mode and my_list['title'] != '' else '',
            reply_markup=None if 'no_button' in px_mode else await image_keyboard(query, my_list),
        )
        return result
    return None


async def inline_pixiv(client, inline_query):
    """Show Pixiv artworks"""
    query = inline_query.query
    if not query:
        return

    offset = inline_query.offset
    pid = int(offset) if offset else 0

    px_mode, keywords = await clean_up_tags(query, PIXIV_MODE, '.px')
    px_mode = await get_user_setting(inline_query, px_mode)
    lists = await get_pixiv_list(keywords, pid, px_mode)

    limit = 50 if len(lists) == 50 and 'illust_detail' not in px_mode else 30
    results = []

    if pid == 0 and not lists:
        return await not_found_msg(client, inline_query)

    for my_list in lists:
        result = await inline_query_result(my_list, query, px_mode)
        if result:
            results.append(result)

    try:
        next_offset = None
        if 'illust_detail' not in px_mode or ('illust_detail' in px_mode and len(lists) == 50):
            next_offset = str(pid + limit)

        await client.answer_inline_query(
            inline_query.id, 
            results=results, 
            cache_time=0, 
            is_gallery=True, 
            next_offset=next_offset)
            
    except Exception as err:
        logging.error(err, exc_info=True)


async def get_px_file(url):
    return await get_pixiv_file(url)

