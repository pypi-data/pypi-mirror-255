import pandas as pd
import streamlit as st

from test_tele.datas import database as dbs
from test_tele.datas import db_helper as dbh
from test_tele.config import CONFIG, read_config, write_config
from test_tele.web_ui.password import check_password
from test_tele.web_ui.utils import *


CONFIG = read_config()

st.set_page_config(
    page_title="Bot Users",
    page_icon="⭐"
)

hide_st(st)


def check_user_settings_data():
    query = dbh.Query()
    user_exists = None

    users = query.read_datas('users', ['chat_id'])
    if users:
        user_exists = [user[0] for user in users]
    
    settings = query.read_datas('settings', ['chat_id'])
    if settings:
        for sett in settings:
            if not user_exists:
                query.delete_data('settings')
            elif sett[0] not in user_exists:
                query.delete_data('settings', f'chat_id = {sett[0]}')


def save_datas(table, conn, keys, data_iter):
    db = dbs.Database()
    db.drop_table(table.name)
    db.create_tables()

    data = [dict(zip(keys, row)) for row in data_iter]
    for x in data:
        if table.name == 'admins':
            try:
                print("sampe sini%s")
                id_admin, chat_id, username, role = None, x['chat_id'], x['username'], x['role']
                add_admin(id_admin, chat_id, username, role)
            except Exception as err:
                print("malah error: ", err)
                continue
        elif table.name == 'users':
            try:
                chat_id, username, firstname, is_subscriber, is_full_subscriber, is_block = int(x['chat_id']), x['username'], x['firstname'], x['is_subscriber'], x['is_full_subscriber'], x['is_block']
                update_user(chat_id, username, firstname, bool_to_int(is_subscriber), bool_to_int(is_full_subscriber), bool_to_int(is_block))
            except:
                continue
        elif table.name == 'settings':
            try:
                chat_id, lang, def_inline, caption, keyboard = int(x['chat_id']), x['lang'], x['def_inline'], x['caption'], x['keyboard']
                update_setting(chat_id, lang, def_inline, bool_to_int(caption), bool_to_int(keyboard))
            except:
                continue


@st.cache_resource(show_spinner="Loading admins")
def get_data_admins():
    query = dbh.Query()
    admins = query.read_datas('admins')
    if admins:
        list_admin = []
        admin_dict = {}
        for admin in admins:
            admin_dict = {
                "admin_id": str(admin[0]),
                "chat_id": str(admin[1]) if admin[1] else None,
                "username": admin[2],
                "role": admin[3]
            }
            list_admin.append(admin_dict)
        return list_admin
    else:
        return [{"admin_id": 1, "chat_id": None, "username": None, "role": 'admin'}]


def add_admin(id_admin, chat_id = None, username = None, role = 'admin'):
    query = dbh.Query()
    if chat_id and str(chat_id).isdigit():
        chat_id = int(chat_id)
    else:
        chat_id = None  
    
    if not query.read_datas('admins', None, f"username = '{username}'"):
        if not id_admin:
            try:
                admins = query.read_datas('admins', ['admin_id'])
                id_admin = max(admins, key=lambda x: x[0])[0] + 1
            except:
                id_admin = 1
        fields = ['admin_id', 'chat_id', 'username', 'role']
        values = [id_admin, chat_id, username, role]
        query.create_data('admins', fields, values)
        return True
    return False


def tab_admins():
    admins = get_data_admins()
    savetable = False
    refresh_btn = st.button("🔄", key='refresh_admins')

    if refresh_btn:
        refresh_data(st)

    df = pd.DataFrame(admins)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("admin_id", "username", "chat_id", "role"),
        column_config={
            "admin_id": st.column_config.TextColumn("No", default=int(len(df) + 1), disabled=True),
            "username": "Username",
            "chat_id": st.column_config.TextColumn("User ID", validate='^[0-9]+$'),
            "role": st.column_config.SelectboxColumn("Role", default='admin', required=True, options=['admin', 'programmer'])
        },
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True,
        key='data_admins'
    )
    
    simpan_btn = st.button('💾', key='save_admins')

    if simpan_btn:
        savetable = True

    if savetable:
        savetable = False
        edited_df.to_sql('admins', ENGINE, if_exists='append', index=False, method=save_datas)
        refresh_data(st)


@st.cache_resource(show_spinner="Loading users")
def get_data_users():
    query = dbh.Query()
    users = query.read_datas('users')

    if users:
        list_user = []
        user_dict = {}
        for user in users:
            user_dict = {
                "user_id": str(user[0]),
                "chat_id": str(user[1]),
                "username": user[2],
                "firstname": user[3],
                "is_subscriber": False if user[4] == 0 else True,
                "is_full_subscriber": False if user[5] == 0 else True,
                "is_block": False if user[6] == 0 else True
            }
            list_user.append(user_dict)
        return list_user
    else:
        return [{"user_id": 1, "chat_id": None, "username": None, "firstname": None, "is_subscriber": False, "is_full_subscriber": False, "is_block": False}]


def update_user(chat_id, username, firstname, is_subscriber, is_full_subscriber, is_block):
    query = dbh.Query()

    if not query.read_datas('users', None, 'chat_id = %s OR username = %s', [chat_id, username]):
        fields = ["chat_id", "username", "firstname", "is_subscriber", "is_full_subscriber", "is_block"]
        values = [chat_id, username, firstname, is_subscriber, is_full_subscriber, is_block]
        query.create_data('users', fields, values)
        return True
    return False


def add_user(user: list):
    query = dbh.Query()

    if not query.read_datas('users', None, 'chat_id = %s OR username = %s', [user[2], user[3]]):
        fields = ["chat_id", "username", "firstname", "is_subscriber", "is_full_subscriber", "is_block"]
        values = [user[2], user[3], user[4], user[5], user[6], user[7]]
        query.create_data('users', fields, values)
        
        fields_sett = ["lang", "def_inline", "caption", "keyboard", "excluded_tags", "chat_id"]
        values_sett = [user[9], user[10], user[11], user[12], user[13], user[2]]
        query.create_data('settings', fields_sett, values_sett)
        return True
    return False


def tab_users():
    users = get_data_users()
    savetable = False
    
    cols = st.columns([1,1,7])
    with cols[0]:
        refresh_btn = st.button("🔄", key='refresh_users')
    with cols[1]:
        query = "SELECT * FROM users JOIN settings ON users.chat_id=settings.chat_id"
        nama_file = 'user_datas.csv'
        export_sqlite_to_csv(query, nama_file)
        with open(nama_file, "rb") as file:
            st.download_button(f"📤", data=file, file_name=nama_file)
 
    if refresh_btn:
        refresh_data(st)

    df = pd.DataFrame(users)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("username", "chat_id", "firstname", "is_subscriber", "is_full_subscriber", "is_block"),
        column_config={
            "username": "Username",
            "chat_id": st.column_config.TextColumn("User ID", validate='^[0-9]+$'),
            "firstname": st.column_config.TextColumn("First Name"),
            "is_subscriber": st.column_config.CheckboxColumn("Premium", default=False),
            "is_full_subscriber": st.column_config.CheckboxColumn("Full Premium", default=False),
            "is_block": st.column_config.CheckboxColumn("Block", default=False)
        },
        num_rows="dynamic", 
        disabled = ["username", "chat_id", "firstname"],
        use_container_width=True, 
        hide_index=False,
        key='data_users'
    )
    
    simpan_btn = st.button('💾', key='save_users')
    
    if simpan_btn:
        savetable = True

    if savetable:
        savetable = False
        edited_df.to_sql('users', ENGINE, if_exists='append', index=False, method=save_datas)
        refresh_data(st)


@st.cache_resource(show_spinner="Loading user settings")
def get_data_user_settings():
    query = dbh.Query()
    settings = query.read_datas('settings')

    if settings:
        user_settings = query.read_datas(
            'users JOIN settings ON users.chat_id = settings.chat_id ',
            ['settings.sett_id', 'users.chat_id', 'users.firstname', 'settings.lang', 'settings.def_inline', 'settings.caption', 'settings.keyboard']
        )

        list_user = []
        user_dict = {}
        for sett in user_settings:
            user_dict = {
                "chat_id": str(sett[1]),
                "firstname": sett[2],
                "lang": sett[3],
                "def_inline": sett[4],
                "caption": False if sett[5] == 0 else True,
                "keyboard": False if sett[6] == 0 else True
            }
            list_user.append(user_dict)
        return list_user
    else:
        return [{"chat_id": None, "firstname": None, "lang": 'en', "def_inline": 'Gelbooru', "caption": True, "keyboard": True}]


def update_setting(chat_id, lang, def_inline, caption, keyboard):
    query = dbh.Query()

    if not query.read_datas('settings', None, 'chat_id = %s', [chat_id]):
        fields = ['lang', 'def_inline', 'caption', 'keyboard', 'chat_id']
        values = [lang, def_inline, caption, keyboard, chat_id]
        query.create_data('settings', fields, values)
        return True
    return False


def tab_user_settings():
    users = get_data_user_settings()
    savetable = False
    refresh_btn = st.button("🔄", key='refresh_user_settings')
        
    if refresh_btn:
        refresh_data(st)

    df = pd.DataFrame(users)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("chat_id", "firstname", "lang", "def_inline", "caption", "keyboard"),
        column_config={
            "chat_id": st.column_config.TextColumn("User ID", validate='^[0-9]+$'),
            "firstname": st.column_config.TextColumn("First Name"),
            "lang": st.column_config.SelectboxColumn("Languange", default='en', required=True, options=['en', 'id', 'ru', 'zh']),
            "def_inline": st.column_config.SelectboxColumn("Default Inline", required=True, default=False, options=['Gelbooru', 'Konachan']),
            "caption": st.column_config.CheckboxColumn("Caption", default=False),
            "keyboard": st.column_config.CheckboxColumn("Keyboard", default=False)
        },
        num_rows="fixed", 
        use_container_width=True, 
        hide_index=False,
        disabled=["chat_id", "firstname"],
        key='data_user_settings'
    )
    
    simpan_btn = st.button('💾', key='save_user_settings')
    
    if simpan_btn:
        savetable = True

    if savetable:
        savetable = False
        edited_df.to_sql('settings', ENGINE, if_exists='append', index=False, method=save_datas)
        refresh_data(st)


@st.cache_resource(show_spinner="Loading user preferences")
def get_data_user_preferences():
    query = dbh.Query()
    settings = query.read_datas('settings')

    if settings:
        user_settings = query.read_datas(
            'users JOIN settings ON users.chat_id = settings.chat_id ',
            ['settings.sett_id', 'users.chat_id', 'users.firstname', 'settings.excluded_tags']
        )

        list_user = []
        user_dict = {}
        for sett in user_settings:
            tags = None
            if sett[3]:
                tags = sett[3].split(", ")
            user_dict = {
                "chat_id": str(sett[1]),
                "firstname": sett[2],
                "excluded_tags": tags
            }
            list_user.append(user_dict)
        return list_user
    else:
        return [{"chat_id": None, "firstname": None, "excluded_tags": None}]


def tab_user_preferences():
    users = get_data_user_preferences()
    refresh_btn = st.button("🔄", key='refresh_user_preferences')
        
    if refresh_btn:
        refresh_data(st)

    df = pd.DataFrame(users)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("chat_id", "firstname", "excluded_tags"),
        column_config={
            "chat_id": st.column_config.TextColumn("User ID", validate='^[0-9]+$'),
            "firstname": st.column_config.TextColumn("First Name"),
            "excluded_tags": st.column_config.ListColumn("Excluded Tags", width='large')
        },
        num_rows="fixed", 
        use_container_width=True, 
        hide_index=False,
        disabled = True,
        key='data_user_preferences'
    )
    

if check_password(st):
    check_user_settings_data()  
    tab1, tab2, tab3, tab4 = st.tabs(["Admins", "Users", "User Settings", "User Preferences"])

    with tab1:
        with st.expander("Import Admin"):
            raw_data = None
            raw_data, df = tampilan_import(st, raw_data, 'import_admin', 'cb_admin')
                
            if raw_data and st.button("💾 Add All", key="add_admins"):
                try:
                    for row in df.itertuples():
                        add_admin(None, row[3] if row[3] != 'nan' else None, row[2], row[4])
                    st.success('All admins added successfully', icon="✅")
                except Exception as e:
                    st.error("An error occured while adding the data!", e, icon="🚨")
        tab_admins()

    with tab2:
        with st.expander("Import User"):
            raw_data = None
            raw_data, df = tampilan_import(st, raw_data, 'import_user', 'cb_user')
                
            if raw_data and st.button("💾 Add All", key="add_users"):
                try:
                    for row in df.itertuples():
                        add_user(row)
                    st.success('All users added successfully', icon="✅")
                except Exception as e:
                    st.error("An error occured while adding the data!", e, icon="🚨")
        tab_users()

    with tab3:
        tab_user_settings()
    
    with tab4:
        tab_user_preferences()
