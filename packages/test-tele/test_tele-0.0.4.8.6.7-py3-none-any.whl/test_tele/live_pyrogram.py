import asyncio
from test_tele.config import CONFIG
from pyrogram import Client, compose, idle

api_id = CONFIG.login.API_ID
api_hash = CONFIG.login.API_HASH
bot_token = CONFIG.login.BOT_TOKEN
session_str = CONFIG.login.PYROGRAM_SESSION_STRING

USER = Client("user_pyro_bot", session_string=session_str, in_memory=True)
BOT = Client("my_bot", api_id=api_id, api_hash=api_hash, in_memory=True, bot_token=bot_token)
PYRO_APPS = []