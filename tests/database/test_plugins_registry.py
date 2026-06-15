import sqlite3

from database.connection import init_schema
from database.plugins_registry import (
    archive_plugin,
    count_active_plugins,
    create_plugin,
    fetch_configured_plugins,
    update_plugin,
)
from plugins.plugin import Plugin


class _SamplePlugin(Plugin):
    DEFAULT_NAME = "Sample Plugin"

    def get_description(self):
        return "test"

    def run(self, user_input_list):
        return user_input_list


def _memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def test_count_active_plugins_is_zero_on_empty_db():
    conn = _memory_db()
    assert count_active_plugins(conn) == 0


def test_create_plugin_uses_defaults_for_optional_fields():
    conn = _memory_db()
    row = create_plugin(conn, "_SamplePlugin")

    assert row["name"] == "_SamplePlugin"
    assert row["custom_name"] == ""
    assert row["options"] == "{}"
    assert row["config_version"] == 1
    assert row["archived"] == 0


def test_create_plugin_returns_new_row():
    conn = _memory_db()
    row = create_plugin(conn, "SamplePlugin", "My label", '{"key": "value"}')

    assert row["custom_name"] == "My label"
    assert row["options"] == '{"key": "value"}'
    assert row["config_version"] == 1


def test_update_plugin_increments_config_version():
    conn = _memory_db()
    row = create_plugin(conn, "SamplePlugin", "v1", "{}")
    updated = update_plugin(conn, row["id"], "v2", '{"a": 1}')

    assert updated["custom_name"] == "v2"
    assert updated["options"] == '{"a": 1}'
    assert updated["config_version"] == 2


def test_archive_plugin_hides_from_fetch_configured():
    conn = _memory_db()
    row = create_plugin(conn, "SamplePlugin", "", "{}")
    archive_plugin(conn, row["id"])

    assert count_active_plugins(conn) == 0
    assert fetch_configured_plugins(conn) == []
