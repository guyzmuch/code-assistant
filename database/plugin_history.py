import json
from datetime import datetime, timezone

from plugins.plugin import Plugin


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
