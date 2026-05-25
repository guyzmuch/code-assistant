import sqlite3
from datetime import datetime, timezone

from database.connection import init_schema
from database.plugin_history import (
    fetch_recent_plugin_history,
    format_history_timestamp,
    history_row_title,
)


def _memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def _insert_history(conn, *, plugin_name, label, timestamp, input_text="", output_text=""):
    conn.execute(
        """
        INSERT INTO plugin_history
            (input, output, plugin_name, label, configuration, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (input_text, output_text, plugin_name, label, "{}", timestamp),
    )
    conn.commit()


def test_fetch_recent_plugin_history_returns_newest_first_with_limit():
    conn = _memory_db()
    _insert_history(
        conn,
        plugin_name="A",
        label="",
        timestamp="2026-01-01T10:00:00+00:00",
    )
    _insert_history(
        conn,
        plugin_name="B",
        label="",
        timestamp="2026-01-03T10:00:00+00:00",
    )
    _insert_history(
        conn,
        plugin_name="C",
        label="",
        timestamp="2026-01-02T10:00:00+00:00",
    )

    rows = fetch_recent_plugin_history(conn, limit=2)

    assert len(rows) == 2
    assert rows[0]["plugin_name"] == "B"
    assert rows[1]["plugin_name"] == "C"


def test_history_row_title_uses_label_when_present():
    row = {
        "label": "My plugin",
        "plugin_name": "default_name",
        "timestamp": "2026-05-25T12:30:00+00:00",
    }
    title = history_row_title(row)
    assert title.startswith("My plugin — ")
    assert "2026-05-25" in title


def test_history_row_title_falls_back_to_plugin_name():
    row = {
        "label": "",
        "plugin_name": "JoinBySeparator",
        "timestamp": "2026-05-25T12:30:00+00:00",
    }
    assert history_row_title(row).startswith("JoinBySeparator — ")


def test_format_history_timestamp_parses_utc_iso():
    formatted = format_history_timestamp(
        datetime(2026, 5, 25, 12, 30, tzinfo=timezone.utc).isoformat()
    )
    assert len(formatted) == 16
    assert formatted[4] == "-"
