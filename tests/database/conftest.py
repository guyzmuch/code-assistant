import sqlite3

from app.context import init
from database.connection import init_schema


def memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    init(conn, None, None)
    return conn
