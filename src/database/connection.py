import sqlite3
from contextlib import contextmanager

from paths import USER_DATA_DIR

PLUGINS_DB_PATH = USER_DATA_DIR / "plugins.db"


def _table_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _ensure_column(cursor, table, column, definition):
    if column not in _table_columns(cursor, table):
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


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
            archived INTEGER,
            show_in_panel INTEGER NOT NULL DEFAULT 1
        )""")

        _ensure_column(
            cursor,
            "plugins",
            "show_in_panel",
            "INTEGER NOT NULL DEFAULT 1",
        )

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
