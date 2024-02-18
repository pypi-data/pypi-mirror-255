import json
import yaml

import streamlit as st

from config import CONFIG_FILE_NAME, read_config, write_config
from config_bot import read_bot_config, write_bot_config
from utils import platform_info
from password import check_password
from test_tele.web_ui.utils import *

CONFIG = read_config()
BOT_CONFIG = read_bot_config()

st.set_page_config(
    page_title="Advanced",
    page_icon="🔬",
)
hide_st(st)

if check_password(st):

    st.warning("This page is for developers and advanced users.")
    if st.checkbox("I agree"):

        with st.expander("Version & Platform"):
            st.code(platform_info())

        with st.expander("Configuration"):
            with open(CONFIG_FILE_NAME, "r") as file:
                data = json.loads(file.read())
                dumped = json.dumps(data, indent=3)
            st.download_button(
                f"Download config json", data=dumped, file_name=CONFIG_FILE_NAME
            )
            st.json(data)

        with st.expander("Special Options for Live Mode"):
            CONFIG.live.sequential_updates = st.checkbox(
                "Enforce sequential updates", value=CONFIG.live.sequential_updates
            )

            CONFIG.live.delete_on_edit = st.text_input(
                "Delete a message when source edited to",
                value=CONFIG.live.delete_on_edit,
            )
            st.write(
                "When you edit the message in source to something particular, the message will be deleted in both source and destinations."
            )

            if st.button("Save"):
                write_config(CONFIG)

        with st.expander("Bot Configuration"):
            tab1, tab2, tab3 = st.tabs(['Bot', 'Telegraph', 'APIs'])
            with tab1:
                st.info(
                    "Note: For userbots, the commands start with `.` instead of `/`, like `.start` and not `/start`"
                )
                BOT_CONFIG.bot_name = st.text_input(
                    "The Username of the bot", value=BOT_CONFIG.bot_name
                )
                BOT_CONFIG.bot_messages.start = st.text_area(
                    "Bot's Reply to /start command", value=BOT_CONFIG.bot_messages.start
                )
                BOT_CONFIG.bot_messages.bot_help = st.text_area(
                    "Bot's Reply to /help command", value=BOT_CONFIG.bot_messages.bot_help
                )
            with tab2:
                BOT_CONFIG.telegraph.short_name = st.text_input(
                    "Telegraph short name", value=BOT_CONFIG.telegraph.short_name
                )
                BOT_CONFIG.telegraph.access_token = st.text_input(
                    "Telegraph access token", value=BOT_CONFIG.telegraph.access_token
                )
                BOT_CONFIG.telegraph.auth_url = st.text_input(
                    "Telegraph auth url", value=BOT_CONFIG.telegraph.auth_url
                )
                BOT_CONFIG.telegraph.prefix = st.text_area(
                    "Prefix for title", value=BOT_CONFIG.telegraph.prefix
                )
                BOT_CONFIG.telegraph.description = st.text_area(
                    "Description", value=BOT_CONFIG.telegraph.description
                )
            with tab3:
                BOT_CONFIG.apis.postgresql_url = st.text_input(
                    "PostgreSQL URL", value=BOT_CONFIG.apis.postgresql_url
                )
                st.caption("Format : postgresql://<user>:<password>@host:port/database_name")
                BOT_CONFIG.apis.pixiv_refresh_token = st.text_input(
                    "Pixiv refresh_token", value=BOT_CONFIG.apis.pixiv_refresh_token
                )
                BOT_CONFIG.apis.gelbooru_api_credentials = st.text_input(
                    "Gelbooru API Access Credentials", value=BOT_CONFIG.apis.gelbooru_api_credentials
                )
            
            if st.button("Save Bot Config"):
                write_bot_config(BOT_CONFIG)
                