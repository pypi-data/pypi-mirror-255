import psycopg2

from test_tele.config_bot import BOT_CONFIG


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(BOT_CONFIG.apis.postgresql_url)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # subscriber != donator : 0 False 1 True
        # full_subscriber : 0 False 1 True (will join group)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                            user_id SERIAL PRIMARY KEY,
                            chat_id integer null,
                            username text null,
                            firstname text null,
                            is_subscriber integer null,
                            is_full_subscriber integer null,
                            is_block integer null
                        )''')
        

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS admins(
                            admin_id integer primary key,
                            chat_id integer null,
                            username text null,
                            role text null
                        )''')
        
        # caption : 0 False 1 True
        # keyboard : 0 False 1 True
        # def_inline : gelbooru | konachan | realbooru | aibooru
        # lang : id | en | ru | zh
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings(
                            sett_id SERIAL PRIMARY KEY,
                            lang text null,
                            def_inline text null,
                            caption integer null,
                            keyboard integer null,
                            excluded_tags text null,
                            chat_id integer null
                        )''')
        
        # safe username of public channel
        # will grab any username inserted, became my own database
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS links(
                            link_id SERIAL PRIMARY KEY,
                            url text null,
                            type text null,
                            notes text null
                        )''')
        
        # safe messages
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages(
                            msg_id SERIAL PRIMARY KEY,
                            id integer null,
                            entity text null,
                            link text null,
                            type text null
                        )''')
        
        self.conn.commit()
        self.conn.close()
        

    # Hapus table
    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()

