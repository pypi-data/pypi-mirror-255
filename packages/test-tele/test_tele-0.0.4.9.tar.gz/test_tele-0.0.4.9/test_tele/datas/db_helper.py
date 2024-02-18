import psycopg2

from test_tele.config_bot import BOT_CONFIG


class Query:
    def __init__(self):
        self.query = ''
        self.values = None

    # Add new data
    def create_data(self, table_name, fields, values):
        placeholders = ', '.join(['%s' for _ in values])
        self.query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders}) RETURNING {', '.join(fields)}"
        self.values = values
        self.dml()

    # Read existed data
    def read_datas(self, table_name, fields=None, condition=None, condition_values=None):
        self.query = f"SELECT {', '.join(fields) if fields else '*'} FROM {table_name}"
        if condition:
            self.query += f" WHERE {condition}"
        self.values = condition_values
        return self.dml(False)

    # Change value existed data
    def update_data(self, table_name, fields, values, condition=None, condition_values=None):
        set_values = ', '.join([f"{field} = '{value}'" for field, value in zip(fields, values)])
        self.query = f"UPDATE {table_name} SET {set_values}"
        if condition:
            self.query += f" WHERE {condition}"

        self.values = condition_values
        self.dml()

    # Detele existed data
    def delete_data(self, table_name, condition=None, condition_values=None):
        self.query = f"DELETE FROM {table_name}"
        if condition:
            self.query += f" WHERE {condition}"
        
        self.values = condition_values
        self.dml()

    def dml(self, commit=True):
        # print(self.query, self.values)
        try:
            conn = psycopg2.connect(BOT_CONFIG.apis.postgresql_url)
            cur = conn.cursor()

            if self.values is not None:
                cur.execute(self.query, self.values)
            else:
                cur.execute(self.query)
            if not commit:
                rows = cur.fetchall()
                return rows
            else:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()