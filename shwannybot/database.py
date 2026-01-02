import sqlite3

conn = sqlite3.connect('voice-chat.db')
c = conn.cursor()

user_list = []

def create_table():
    c.execute(f"CREATE TABLE data (user text, start_time real ,end_time real, duration real)")
    conn.commit()

def table_exist_check(table_name):
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return c.fetchone() is not None


def record_insert(table_name, name, start_time, end_time, duration):
    c.execute(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?) ", (name, start_time, end_time, duration ))
    conn.commit()


def table_wipe(table_name):
    c.execute(f"DROP TABLE {table_name}")
    conn.commit()


