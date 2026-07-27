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
            show_in_panel INTEGER NOT NULL DEFAULT 1,
            chain_id TEXT,
            chain_position INTEGER
        )""")

        _ensure_column(
            cursor,
            "plugins",
            "show_in_panel",
            "INTEGER NOT NULL DEFAULT 1",
        )
        # Chain grouping: a chain is several plugins rows sharing a chain_id.
        # chain_position 0 is the chain header; positions >= 1 are its steps.
        # Standalone plugins leave both columns NULL.
        _ensure_column(cursor, "plugins", "chain_id", "TEXT")
        _ensure_column(cursor, "plugins", "chain_position", "INTEGER")

        # Only one active row may occupy a given (chain_id, position); archived
        # step rows are excluded so a chain can be edited without violating it.
        cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_plugins_chain_position
        ON plugins(chain_id, chain_position)
        WHERE chain_id IS NOT NULL AND archived = 0
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plugin_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input TEXT,
            output TEXT,
            plugin_id INTEGER,
            config_version INTEGER,
            timestamp TEXT,
            execution_id TEXT,
            execution_position INTEGER
        )""")
        # Execution grouping: one run shares an execution_id. execution_position
        # 0 is the run summary; positions >= 1 are chain step results.
        _ensure_column(cursor, "plugin_history", "execution_id", "TEXT")
        _ensure_column(cursor, "plugin_history", "execution_position", "INTEGER")
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
