from test_tele.datas import db_helper as dbh
from pyrogram.types import (InlineQueryResultArticle, InlineQueryResultPhoto, InlineQueryResultVideo, InlineKeyboardMarkup, 
                            InlineKeyboardButton, InputTextMessageContent, InlineQueryResultAnimation, InputTextMessageContent)

QUERY = dbh.Query()

async def not_found_msg(client, inline_query):
    err_result = [
        InlineQueryResultArticle(
            'No results found', InputTextMessageContent(message_text='No results found'), 
            id='noresults', description='Please try again with different tags')
    ]
    await client.answer_inline_query(
        inline_query.id,
        results=err_result
    )
    return


async def get_user_setting(event, mode:dict = {}):
    db = QUERY
    user = db.read_datas('settings', ['caption', 'keyboard'], 'chat_id = %s', [event.from_user.id])
    if user:
        user = user[0]
        if not user[0]: # caption 0 | false | no caption
            mode.update({"no_tag": True})
        if not user[1]: # keyboard 0 | false | no button
            mode.update({"no_button": True})

    return mode