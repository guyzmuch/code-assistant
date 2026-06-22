from datetime import datetime, timezone

from app.context import db_connection
from app.plugins_loader import discover_plugin_classes


def format_history_timestamp(timestamp_iso: str) -> str:
    dt = datetime.fromisoformat(timestamp_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone().strftime("%Y-%m-%d %H:%M")


def _default_name_for_class(class_name: str) -> str:
    for plugin_class in discover_plugin_classes():
        if plugin_class.__name__ == class_name:
            return plugin_class.DEFAULT_NAME
    return class_name


def _version_suffix(row) -> str:
    stored_version = row["config_version"]
    current_version = row["current_config_version"]
    if current_version is not None and stored_version == current_version:
        return "latest version"
    return f"v{stored_version}"


def _history_label(row) -> str:
    custom_name = row["custom_name"]
    if custom_name:
        return custom_name
    class_name = row["name"]
    if class_name:
        return _default_name_for_class(class_name)
    return "Unknown plugin"


def history_row_title(row):
    label = _history_label(row)
    version_suffix = _version_suffix(row)
    return (
        f"{format_history_timestamp(row['timestamp'])} — "
        f"{label} ({version_suffix})"
    )


def fetch_recent_plugin_history(limit=10):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            h.id,
            h.input,
            h.output,
            h.plugin_id,
            h.config_version,
            h.timestamp,
            p.name,
            p.custom_name,
            p.config_version AS current_config_version
        FROM plugin_history h
        LEFT JOIN plugins p ON p.id = h.plugin_id
        ORDER BY h.timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cursor.fetchall()


def delete_plugin_history_entry(record_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plugin_history WHERE id = ?", (record_id,))
    conn.commit()


def save_plugin_execution(
    plugin_id,
    input_text,
    output_text,
    config_version,
):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO plugin_history
            (input, output, plugin_id, config_version, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            input_text,
            output_text,
            plugin_id,
            config_version,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
