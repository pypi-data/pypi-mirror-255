import uuid 
import logging

from pyrogram.types import (InlineQueryResultArticle, InlineQueryResultPhoto, InlineQueryResultVideo, InlineKeyboardMarkup, 
                            InlineKeyboardButton, InputTextMessageContent, InlineQueryResultAnimation, InputTextMessageContent)

from test_tele.features.extractors.realperson import *
from test_tele.features.pyrogram.utils import not_found_msg, get_user_setting


async def image_keyboard(query: str, my_list: list[str]) -> InlineKeyboardMarkup:
    buttons = [[
                InlineKeyboardButton("💾" ,
                                     callback_data=f"rp {my_list['filename']}.{my_list['extension']}"),
                InlineKeyboardButton("🔄",
                                     switch_inline_query_current_chat=query),
            ]]
    return InlineKeyboardMarkup(buttons)


async def inline_query_result(my_list, query, mode):
    caption = (
       f'Category : Real Person\n'
       f'Tags : {my_list["tags"]}'
    )
    
    if my_list['extension'] in IMG_EXT:
        result = InlineQueryResultPhoto(
            photo_url=my_list['img_url'],
            thumb_url=my_list['thumbnail'],
            id=str(uuid.uuid4()) + my_list['id'][:3],
            caption=caption if 'no_tag' not in mode else '',
            reply_markup=None if 'no_button' in mode else await image_keyboard(query, my_list),
        )
        return result
    elif my_list['extension'] in VID_EXT:
        result = InlineQueryResultVideo(
            video_url=my_list['img_url'].replace(".webm", ".mp4"),
            thumb_url=my_list['thumbnail'],
            title=f'Video {my_list["width"]}x{my_list["height"]}',
            id=str(uuid.uuid4()) + my_list['id'][:3],
            mime_type='video/mp4',
            caption=caption if 'no_tag' not in mode else '',
            reply_markup=None if 'no_button' in mode else await image_keyboard(query, my_list),
        )
        return result
    elif my_list['extension'] in GIF_EXT:
        result = InlineQueryResultAnimation(
            animation_url=my_list['img_url'],
            thumb_url=my_list['thumbnail'],
            id=str(uuid.uuid4()) + my_list['id'][:3],
            caption=caption if 'no_tag' not in mode else '',
            reply_markup=None if 'no_button' in mode else await image_keyboard(query, my_list),
        )
        return result
    return None


async def inline_realperson(client, inline_query):
    """Show real person nude"""
    query = inline_query.query
    if not query:
        return

    offset = inline_query.offset
    pid = int(offset) if offset else 0
    
    rp_mode, keywords = await clean_up_tags(query, [], '.rp')
    rp_mode = await get_user_setting(inline_query, rp_mode)
    lists = await get_nude_list(keywords, pid, rp_mode)

    results = []
    if pid == 0 and not lists:
        return await not_found_msg(client, inline_query)

    for my_list in lists:
        result = await inline_query_result(my_list, query, rp_mode)

        if result:
            results.append(result)
    try:
        await client.answer_inline_query(
            inline_query.id,
            results=results,
            cache_time=60,
            is_gallery=True,
            next_offset=str(pid + OFFSET_PID)
        )
    except Exception as err:
        logging.error(err, exc_info=True)

