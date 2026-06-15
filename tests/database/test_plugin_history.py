import sqlite3
from datetime import datetime, timezone

from database.connection import init_schema
from database.plugin_history import (
    delete_plugin_history_entry,
    fetch_recent_plugin_history,
    format_history_timestamp,
    history_row_title,
    save_plugin_execution,
)
from database.plugins_registry import create_plugin, update_plugin


def _memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def _insert_history(
    conn,
    *,
    plugin_id,
    config_version,
    timestamp,
    input_text="",
    output_text="",
):
    conn.execute(
        """
        INSERT INTO plugin_history
            (input, output, plugin_id, config_version, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (input_text, output_text, plugin_id, config_version, timestamp),
    )
    conn.commit()


def test_fetch_recent_plugin_history_returns_newest_first_with_limit():
    conn = _memory_db()
    plugin = create_plugin(conn, "HashLines", "", "{}")
    _insert_history(
        conn,
        plugin_id=plugin["id"],
        config_version=1,
        timestamp="2026-01-01T10:00:00+00:00",
    )
    _insert_history(
        conn,
        plugin_id=plugin["id"],
        config_version=1,
        timestamp="2026-01-03T10:00:00+00:00",
    )
    _insert_history(
        conn,
        plugin_id=plugin["id"],
        config_version=1,
        timestamp="2026-01-02T10:00:00+00:00",
    )

    rows = fetch_recent_plugin_history(conn, limit=2)

    assert len(rows) == 2
    assert rows[0]["timestamp"].startswith("2026-01-03")
    assert rows[1]["timestamp"].startswith("2026-01-02")


def test_history_row_title_uses_custom_name_and_latest_version():
    conn = _memory_db()
    plugin = create_plugin(conn, "HashLines", "My plugin", "{}")
    row = {
        "custom_name": "My plugin",
        "name": "HashLines",
        "config_version": 1,
        "current_config_version": 1,
        "timestamp": "2026-05-25T12:30:00+00:00",
    }
    title = history_row_title(row, conn)
    assert title.startswith("2026-05-25")
    assert "My plugin" in title
    assert "(latest version)" in title


def test_history_row_title_shows_version_when_stale():
    conn = _memory_db()
    plugin = create_plugin(conn, "JoinBySeparator", "", "{}")
    update_plugin(conn, plugin["id"], "", '{"separator": ";"}')
    row = {
        "custom_name": "",
        "name": "JoinBySeparator",
        "config_version": 1,
        "current_config_version": 2,
        "timestamp": "2026-05-25T12:30:00+00:00",
    }
    title = history_row_title(row, conn)
    assert "(v1)" in title
    assert "Join by separator" in title


def test_delete_plugin_history_entry_removes_record():
    conn = _memory_db()
    plugin = create_plugin(conn, "HashLines", "", "{}")
    _insert_history(
        conn,
        plugin_id=plugin["id"],
        config_version=1,
        timestamp="2026-01-01T10:00:00+00:00",
    )
    _insert_history(
        conn,
        plugin_id=plugin["id"],
        config_version=1,
        timestamp="2026-01-02T10:00:00+00:00",
    )

    rows = fetch_recent_plugin_history(conn)
    delete_plugin_history_entry(conn, rows[0]["id"])

    remaining = fetch_recent_plugin_history(conn)
    assert len(remaining) == 1
    assert remaining[0]["timestamp"].startswith("2026-01-01")


def test_save_plugin_execution_stores_plugin_id_and_version():
    conn = _memory_db()
    plugin = create_plugin(conn, "HashLines", "Label", '{"algorithm": "sha256"}')

    save_plugin_execution(conn, plugin["id"], "in", "out", plugin["config_version"])

    rows = fetch_recent_plugin_history(conn)
    assert len(rows) == 1
    assert rows[0]["plugin_id"] == plugin["id"]
    assert rows[0]["config_version"] == 1
    assert rows[0]["input"] == "in"
    assert rows[0]["output"] == "out"


def test_format_history_timestamp_parses_utc_iso():
    formatted = format_history_timestamp(
        datetime(2026, 5, 25, 12, 30, tzinfo=timezone.utc).isoformat()
    )
    assert len(formatted) == 16
    assert formatted[4] == "-"
