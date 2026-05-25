import sqlite3
from contextlib import contextmanager


PLUGINS_DB_PATH = "plugins.db"


def init_schema(db_connection):
    cursor = db_connection.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plugins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            activated INTEGER,
            new_plugin INTEGER,
            options TEXT,
            shortcut TEXT,
            custom_name TEXT
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plugin_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input TEXT,
            output TEXT,
            plugin_name TEXT,
            label TEXT,
            configuration TEXT,
            timestamp TEXT
        )""")
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f"Error: {e}")
        raise


@contextmanager
def database_connection(path=PLUGINS_DB_PATH):
    with sqlite3.connect(path) as db_connection:
        db_connection.row_factory = sqlite3.Row
        init_schema(db_connection)
        yield db_connection
