import os
import csv
import psycopg2
import pandas as pd

from io import StringIO
from typing import Dict, List
from sqlalchemy import create_engine

from test_tele.config_bot import BOT_CONFIG

url = BOT_CONFIG.apis.postgresql_url.split("://")[-1]
ENGINE = create_engine("postgresql+psycopg2://" + url)


def get_list(string: str):
    # string where each line is one element
    my_list = []
    for line in string.splitlines():
        clean_line = line.strip()
        if clean_line != "":
            my_list.append(clean_line)
    return my_list


def get_string(my_list: List):
    string = ""
    for item in my_list:
        string += f"{item}\n"
    return string


def dict_to_list(dict: Dict):
    my_list = []
    for key, val in dict.items():
        my_list.append(f"{key}: {val}")
    return my_list


def list_to_dict(my_list: List):
    my_dict = {}
    for item in my_list:
        key, val = item.split(":")
        my_dict[key.strip()] = val.strip()
    return my_dict


def hide_st(st):
    dev = os.getenv("DEV")
    if dev:
        return
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Export dataframe menjadi csv
def export_dataframe(st, dataframe, file_name):
    df = pd.DataFrame(dataframe)
    df.to_csv(f'{file_name}', index=False)
    st.success('Exported successfully', icon="✅")


def bool_to_int(bool_value):
    if bool_value:
        return 1
    else:
        return 0


def refresh_data(st):
    st.cache_resource.clear()
    st.rerun()


def tampilan_import(st, raw_data, key_uploader, key_checkbox):
    datas = st.file_uploader(
        label="Upload file",
        type=['csv'],
        accept_multiple_files=False,
        key=key_uploader
    )

    if datas is not None:
        bytes_data = datas.getvalue()
        raw_data = StringIO(bytes_data.decode('utf-8'))
        st.success('Uploaded successfully', icon="✅")

    if raw_data:
        df = pd.read_csv(datas, index_col=False, delimiter = ',')
        if st.checkbox('Show in tables', key=key_checkbox):
            try:
                st.dataframe(df, use_container_width=True, hide_index=True)
            except:
                st.error("An error occured, please double check your file!", icon="🚨")
    
    if raw_data:
        return raw_data, df
    return False, False


def export_sqlite_to_csv(query, csv_name):
    conn = psycopg2.connect(BOT_CONFIG.apis.postgresql_url)
    cursor = conn.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    with open(csv_name, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(rows)

    conn.close()
