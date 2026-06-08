import json
from datetime import datetime, timezone

from plugins.plugin import Plugin


def format_history_timestamp(timestamp_iso: str) -> str:
    dt = datetime.fromisoformat(timestamp_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone().strftime("%Y-%m-%d %H:%M")


def history_row_title(row) -> str:
    label = row["label"] or row["plugin_name"]
    return f"{format_history_timestamp(row['timestamp'])} — {label}"


def fetch_recent_plugin_history(db_connection, limit=10):
    cursor = db_connection.cursor()
    cursor.execute(
        """
        SELECT id, input, output, plugin_name, label, timestamp
        FROM plugin_history
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cursor.fetchall()


def delete_plugin_history_entry(db_connection, record_id):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM plugin_history WHERE id = ?", (record_id,))
    db_connection.commit()


def save_plugin_execution(db_connection, plugin: Plugin, input_text: str, output_text: str):
    cursor = db_connection.cursor()
    cursor.execute(
        """
        INSERT INTO plugin_history
            (input, output, plugin_name, label, configuration, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            input_text,
            output_text,
            plugin.get_default_name(),
            plugin.custom_name,
            json.dumps(plugin.get_options()),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    db_connection.commit()
