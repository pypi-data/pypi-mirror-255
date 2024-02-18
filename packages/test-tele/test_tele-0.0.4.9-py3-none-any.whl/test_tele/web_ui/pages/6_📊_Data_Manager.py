import pandas as pd
import streamlit as st

from test_tele.datas import db_helper as dbh
from test_tele.config import CONFIG, read_config, write_config
from test_tele.web_ui.password import check_password
from test_tele.web_ui.utils import *


CONFIG = read_config()

st.set_page_config(
    page_title="Data Manager",
    page_icon="📊"
)

hide_st(st)


def save_datas(table, conn, keys, data_iter):
    query = dbh.Query()
    data = [dict(zip(keys, row)) for row in data_iter]

    query.delete_data('links', 'type = %s', [data[-1]['type']])
    for x in data:
        try:
            url, type, notes = x['url'], x['type'], x['notes']
            update_links(url, type, notes)
        except:
            continue


def update_links(url = None, type = None, notes = None):
    query = dbh.Query()

    if url:
        if not query.read_datas('links', None, 'url = %s', [url]):
            fields = ['url', 'type', 'notes']
            values = [url, type, notes]
            query.create_data('links', fields, values)
            return True
        return False
    else:
        query.delete_data('links', 'url = %s', [' '])
        

@st.cache_resource(show_spinner="Loading channel")
def get_data_channels():
    query = dbh.Query()
    pchannels = query.read_datas('links', None, 'type = %s', ['channel'])
    if pchannels:
        list_pchannels = []
        pchannels_dict = {}
        for channel in pchannels:
            pchannels_dict = {
                "url": channel[1],
                "type": channel[2],
                "notes": channel[3]
            }
            list_pchannels.append(pchannels_dict)
        return list_pchannels
    else:
        return [{"url": None, "type": 'channel', "notes": None}]


def tab_channels():
    channels = get_data_channels()
    savetable = False
    refresh_btn = st.button("🔄", key='refresh_channels')

    if refresh_btn:
        refresh_data(st)

    df = pd.DataFrame(channels)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("url", "type", "notes"),
        column_config={
            "url": st.column_config.LinkColumn("Link", width='medium', display_text="https://t\.me/(.+)"),
            "type": st.column_config.TextColumn("Type", default='channel'),
            "notes": st.column_config.TextColumn("Notes", width='small')
        },
        num_rows="dynamic", 
        disabled= ['type'],
        use_container_width=True, 
        hide_index=False,
        key='data_channels'
    )
    
    simpan_btn = st.button('💾', key='save_channels')

    if simpan_btn:
        savetable = True

    if savetable:
        savetable = False
        edited_df.to_sql('links', ENGINE, if_exists='append', index=False, method=save_datas)
        refresh_data(st)


@st.cache_resource(show_spinner="Loading sticker")
def get_data_stickers():
    query = dbh.Query()
    stickers = query.read_datas('links', None, 'type = %s', ['sticker'])
    if stickers:
        list_stickers = []
        stickers_dict = {}
        for sticker in stickers:
            stickers_dict = {
                "url": sticker[1],
                "type": sticker[2],
                "notes": sticker[3]
            }
            list_stickers.append(stickers_dict)
        return list_stickers
    else:
        return [{"url": None, "type": 'sticker', "notes": None}]


def tab_stickers():
    stickers = get_data_stickers()
    savetable = False
    refresh_btn = st.button("🔄", key='refresh_stickers')

    if refresh_btn:
        refresh_data(st)

    df = pd.DataFrame(stickers)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("url", "type", "notes"),
        column_config={
            "url": st.column_config.LinkColumn("Link", width='medium', display_text="https://t\.me/addstickers/(.+)"),
            "type": st.column_config.TextColumn("Type", default='sticker'),
            "notes": st.column_config.TextColumn("Notes", width='small')
        },
        num_rows="dynamic", 
        disabled= ['type'],
        use_container_width=True, 
        hide_index=False,
        key='data_stickers'
    )
    
    simpan_btn = st.button('💾', key='save_stickers')

    if simpan_btn:
        savetable = True

    if savetable:
        savetable = False
        edited_df.to_sql('links', ENGINE, if_exists='append', index=False, method=save_datas)
        refresh_data(st)


@st.cache_resource(show_spinner="Loading addlist")
def get_data_addlists():
    query = dbh.Query()
    addlists = query.read_datas('links', None, 'type = %s', ['addlist'])
    if addlists:
        list_addlists = []
        addlists_dict = {}
        for addlist in addlists:
            addlists_dict = {
                "url": addlist[1],
                "type": addlist[2],
                "notes": addlist[3]
            }
            list_addlists.append(addlists_dict)
        return list_addlists
    else:
        return [{"url": None, "type": 'addlist', "notes": None}]
    

def tab_addlists():
    channels = get_data_addlists()
    savetable = False
    refresh_btn = st.button("🔄", key='refresh_addlists')

    if refresh_btn:
        refresh_data(st)

    df = pd.DataFrame(channels)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("url", "type", "notes"),
        column_config={
            "url": st.column_config.LinkColumn("Link", width='medium', display_text="https://t\.me/(.+)"),
            "type": st.column_config.TextColumn("Type", default='addlist'),
            "notes": st.column_config.TextColumn("Notes", width='small')
        },
        num_rows="dynamic", 
        disabled= ['type'],
        use_container_width=True, 
        hide_index=False,
        key='data_addlists'
    )
    
    simpan_btn = st.button('💾', key='save_addlists')

    if simpan_btn:
        savetable = True

    if savetable:
        savetable = False
        edited_df.to_sql('links', ENGINE, if_exists='append', index=False, method=save_datas)
        refresh_data(st)


if check_password(st):
    tab1, tab2, tab3 = st.tabs(["Public Channels", "Sticker Packs", "Addlist"])

    with tab1:
        with st.expander("Import Channels"):
            raw_data = None
            raw_data, df = tampilan_import(st, raw_data, 'import_channels', 'cb_channels')
                
            if raw_data and st.button("💾 Add All", key="add_channels"):
                try:
                    for row in df.itertuples():
                        update_links(row[2], row[3])
                    st.success('All channels added successfully', icon="✅")
                except Exception as e:
                    st.error("An error occured while adding the data!", e, icon="🚨")
        tab_channels()
    with tab2:
        with st.expander("Import Stickers"):
            raw_data = None
            raw_data, df = tampilan_import(st, raw_data, 'import_stickers', 'cb_stickers')
                
            if raw_data and st.button("💾 Add All", key="add_stickers"):
                try:
                    for row in df.itertuples():
                        update_links(row[2], row[3])
                    st.success('All stickers added successfully', icon="✅")
                except Exception as e:
                    st.error("An error occured while adding the data!", e, icon="🚨")
        tab_stickers()
    with tab3:
        with st.expander("Import Addlist"):
            raw_data = None
            raw_data, df = tampilan_import(st, raw_data, 'import_addlists', 'cb_addlists')
                
            if raw_data and st.button("💾 Add All", key="add_addlists"):
                try:
                    for row in df.itertuples():
                        update_links(row[2], row[3])
                    st.success('All addlists added successfully', icon="✅")
                except Exception as e:
                    st.error("An error occured while adding the data!", e, icon="🚨")
        tab_addlists()


