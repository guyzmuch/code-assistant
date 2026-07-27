import uuid
from datetime import datetime, timezone

from app.context import db_connection
from app.plugins_loader import discover_plugin_classes


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_text(data) -> str:
    """Normalize a plugin input/output for storage.

    Plugins work with lists of lines, but history stores plain text. Accept
    either so callers (Plugin/PluginChain) don't have to join before recording:
    a string is stored as-is, a list is joined with newlines.
    """
    if isinstance(data, str):
        return data
    return "\n".join(data)


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


_HISTORY_SELECT = """
    SELECT
        h.id,
        h.input,
        h.output,
        h.plugin_id,
        h.config_version,
        h.timestamp,
        h.execution_id,
        h.execution_position,
        p.name,
        p.custom_name,
        p.chain_position,
        p.config_version AS current_config_version
    FROM plugin_history h
    LEFT JOIN plugins p ON p.id = h.plugin_id
"""


def fetch_recent_plugin_history(limit=10):
    conn = db_connection()
    cursor = conn.cursor()
    # Only top-level entries: a standalone run, a chain summary, or a legacy row
    # (execution_position NULL). Chain steps (position >= 1) load on expand.
    cursor.execute(
        _HISTORY_SELECT
        + """
        WHERE h.execution_position IS NULL OR h.execution_position = 0
        ORDER BY h.timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cursor.fetchall()


def fetch_execution_steps(execution_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        _HISTORY_SELECT
        + """
        WHERE h.execution_id = ? AND h.execution_position >= 1
        ORDER BY h.execution_position
        """,
        (execution_id,),
    )
    return cursor.fetchall()


def count_execution_steps(execution_id) -> int:
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) FROM plugin_history
        WHERE execution_id = ? AND execution_position >= 1
        """,
        (execution_id,),
    )
    return cursor.fetchone()[0]


def is_chain_history_row(row) -> bool:
    """True when a top-level history row is a chain summary (header at pos 0)."""
    keys = row.keys() if hasattr(row, "keys") else row
    if "chain_position" not in keys:
        return False
    return row["chain_position"] == 0


def delete_plugin_history_entry(record_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plugin_history WHERE id = ?", (record_id,))
    conn.commit()


def delete_plugin_history_execution(execution_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM plugin_history WHERE execution_id = ?", (execution_id,)
    )
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
            (input, output, plugin_id, config_version, timestamp,
             execution_id, execution_position)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """,
        (
            input_text,
            output_text,
            plugin_id,
            config_version,
            _now_iso(),
            uuid.uuid4().hex,
        ),
    )
    conn.commit()


class HistoryRecorder:
    """Persists executions. Injected into Runnable.execute() so plugin/chain
    classes coordinate what to record without importing the database layer."""

    def record_plugin_execution(self, plugin, input_data, output_data):
        save_plugin_execution(
            plugin.id,
            _as_text(input_data),
            _as_text(output_data),
            plugin.config_version,
        )

    def start_chain_execution(self, chain):
        return ChainExecutionRecorder(chain)


class ChainExecutionRecorder:
    """Collects a chain's summary and step rows, then writes them under one
    execution_id in a single transaction with one shared timestamp."""

    def __init__(self, chain):
        self._chain = chain
        self._execution_id = uuid.uuid4().hex
        self._steps = []

    def record_step(self, position, plugin, input_data, output_data):
        self._steps.append((position, plugin, input_data, output_data))

    def finish(self, input_data, output_data):
        conn = db_connection()
        cursor = conn.cursor()
        timestamp = _now_iso()
        cursor.execute(
            """
            INSERT INTO plugin_history
                (input, output, plugin_id, config_version, timestamp,
                 execution_id, execution_position)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                _as_text(input_data),
                _as_text(output_data),
                self._chain.id,
                self._chain.config_version,
                timestamp,
                self._execution_id,
            ),
        )
        for position, plugin, step_input, step_output in self._steps:
            cursor.execute(
                """
                INSERT INTO plugin_history
                    (input, output, plugin_id, config_version, timestamp,
                     execution_id, execution_position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _as_text(step_input),
                    _as_text(step_output),
                    plugin.id,
                    plugin.config_version,
                    timestamp,
                    self._execution_id,
                    position,
                ),
            )
        conn.commit()
        return self._execution_id
