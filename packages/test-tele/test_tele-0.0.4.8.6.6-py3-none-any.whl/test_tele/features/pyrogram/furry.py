import uuid 
import logging

from pyrogram import enums
from pyrogram.types import InputMediaPhoto, InputMediaDocument
from pyrogram.types import (InlineQueryResultArticle, InlineQueryResultPhoto, InlineQueryResultVideo, InlineKeyboardMarkup, 
                            InlineKeyboardButton, InputTextMessageContent, InlineQueryResultAnimation, InputTextMessageContent)

from test_tele.features.extractors.furry import *
from test_tele.features.pyrogram.utils import not_found_msg, get_user_setting


async def image_keyboard(query: str, my_list: list[str]) -> InlineKeyboardMarkup:
    buttons = [[
                InlineKeyboardButton("💾" ,
                                     callback_data=f"fur {my_list['category']},{my_list['id_file']}.{my_list['extension']}"),
                InlineKeyboardButton("🔗",
                                     url=f'https://e6ai.net/posts/{my_list["id"]}'),
                InlineKeyboardButton("🔄",
                                     switch_inline_query_current_chat=query),
            ]]
    return InlineKeyboardMarkup(buttons)


async def inline_query_result(my_list, query, mode):
    caption = (
       f'Artist : {my_list["artist"].replace("`", "")}\n'
       f'Tags : {my_list["tags"]}'
    )

    if my_list['extension'] in GIF_EXT:
        result = InlineQueryResultAnimation(
            animation_url=my_list['img_url'],
            animation_width=my_list['width'],
            animation_height=my_list['height'],
            thumb_url=my_list['thumbnail'],
            id=str(uuid.uuid4()) + my_list['id'][:3],
            caption=caption if 'no_tag' not in mode else '',
            reply_markup=None if 'no_button' in mode else await image_keyboard(query, my_list),
        )
        return result
    elif my_list['extension'] in IMG_EXT:
        result = InlineQueryResultPhoto(
            photo_url=my_list['img_url'],
            thumb_url=my_list['thumbnail'],
            photo_width=my_list['width'],
            photo_height=my_list['height'],
            id=str(uuid.uuid4()) + my_list['id'][:3],
            caption=caption if 'no_tag' not in mode else '',
            reply_markup=None if 'no_button' in mode else await image_keyboard(query, my_list),
        )
        return result
    return None


async def inline_furry(client, inline_query):
    """Show e621 artworks"""
    query = inline_query.query
    if not query:
        return

    offset = inline_query.offset
    pid = int(offset) if offset else 0
    
    fur_mode, keywords = await clean_up_tags(query, FURRY_MODE, '.fur')
    fur_mode = await get_user_setting(inline_query, fur_mode)
    lists = await get_furry_list(keywords, pid, fur_mode)

    results = []
    if pid == 0 and not lists:
        return await not_found_msg(client, inline_query)

    for my_list in lists:
        result = await inline_query_result(my_list, query, fur_mode)

        if result:
            results.append(result)
    try:
        await client.answer_inline_query(
            inline_query.id,
            results=results,
            cache_time=180,
            is_gallery=True,
            next_offset=str(pid + OFFSET_PID)
        )
    except Exception as err:
        logging.error(err, exc_info=True)

