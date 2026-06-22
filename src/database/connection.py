import sqlite3
from contextlib import contextmanager

from paths import SRC_ROOT

PLUGINS_DB_PATH = SRC_ROOT / "plugins.db"


def init_schema(db_connection):
    cursor = db_connection.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plugins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            custom_name TEXT,
            options TEXT,
            shortcut TEXT,
            config_version INTEGER,
            archived INTEGER
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plugin_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input TEXT,
            output TEXT,
            plugin_id INTEGER,
            config_version INTEGER,
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
