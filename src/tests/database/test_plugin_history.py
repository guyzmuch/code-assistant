from datetime import datetime, timezone

from database.plugin_history import (
    ChainExecutionRecorder,
    _as_text,
    delete_plugin_history_entry,
    delete_plugin_history_execution,
    fetch_execution_steps,
    fetch_recent_plugin_history,
    format_history_timestamp,
    history_row_title,
    save_plugin_execution,
)
from database.plugins_registry import (
    create_chain,
    create_plugin,
    fetch_chain_steps,
    update_plugin,
)
from tests.database.conftest import memory_db


class _FakeChain:
    def __init__(self, header):
        self.id = header["id"]
        self.config_version = header["config_version"]


class _FakeStepPlugin:
    def __init__(self, step_row):
        self.id = step_row["id"]
        self.config_version = step_row["config_version"]


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
    conn = memory_db()
    plugin = create_plugin("HashLines", "", "{}")
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

    rows = fetch_recent_plugin_history(limit=2)

    assert len(rows) == 2
    assert rows[0]["timestamp"].startswith("2026-01-03")
    assert rows[1]["timestamp"].startswith("2026-01-02")


def test_history_row_title_uses_custom_name_and_latest_version():
    memory_db()
    row = {
        "custom_name": "My plugin",
        "name": "HashLines",
        "config_version": 1,
        "current_config_version": 1,
        "timestamp": "2026-05-25T12:30:00+00:00",
    }
    title = history_row_title(row)
    assert title.startswith("2026-05-25")
    assert "My plugin" in title
    assert "(latest version)" in title


def test_history_row_title_shows_version_when_stale():
    memory_db()
    plugin = create_plugin("JoinBySeparator", "", "{}")
    update_plugin(plugin["id"], "", '{"separator": ";"}')
    row = {
        "custom_name": "",
        "name": "JoinBySeparator",
        "config_version": 1,
        "current_config_version": 2,
        "timestamp": "2026-05-25T12:30:00+00:00",
    }
    title = history_row_title(row)
    assert "(v1)" in title
    assert "Join by separator" in title


def test_delete_plugin_history_entry_removes_record():
    conn = memory_db()
    plugin = create_plugin("HashLines", "", "{}")
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

    rows = fetch_recent_plugin_history()
    delete_plugin_history_entry(rows[0]["id"])

    remaining = fetch_recent_plugin_history()
    assert len(remaining) == 1
    assert remaining[0]["timestamp"].startswith("2026-01-01")


def test_save_plugin_execution_stores_plugin_id_and_version():
    memory_db()
    plugin = create_plugin("HashLines", "Label", '{"algorithm": "sha256"}')

    save_plugin_execution(plugin["id"], "in", "out", plugin["config_version"])

    rows = fetch_recent_plugin_history()
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


def test_as_text_accepts_string_or_line_list():
    assert _as_text("already text") == "already text"
    assert _as_text(["a", "b", "c"]) == "a\nb\nc"
    assert _as_text([]) == ""


def test_legacy_history_row_without_execution_fields_is_visible():
    conn = memory_db()
    plugin = create_plugin("HashLines", "", "{}")
    _insert_history(
        conn,
        plugin_id=plugin["id"],
        config_version=1,
        timestamp="2026-01-01T10:00:00+00:00",
    )

    rows = fetch_recent_plugin_history()

    assert len(rows) == 1
    assert rows[0]["execution_position"] is None


def test_chain_execution_recorder_groups_summary_and_steps():
    memory_db()
    header = create_chain(
        "Chain",
        [
            {"name": "ChangeCase", "options": "{}"},
            {"name": "JoinBySeparator", "options": "{}"},
        ],
    )
    step_rows = fetch_chain_steps(header["chain_id"])

    recorder = ChainExecutionRecorder(_FakeChain(header))
    recorder.record_step(1, _FakeStepPlugin(step_rows[0]), "a", "A")
    recorder.record_step(2, _FakeStepPlugin(step_rows[1]), "A", "A!")
    execution_id = recorder.finish("a", "A!")

    top = fetch_recent_plugin_history()
    assert len(top) == 1
    assert top[0]["execution_position"] == 0
    assert top[0]["plugin_id"] == header["id"]

    steps = fetch_execution_steps(execution_id)
    assert [s["execution_position"] for s in steps] == [1, 2]


def test_delete_plugin_history_execution_removes_all_rows():
    memory_db()
    header = create_chain("Chain", [{"name": "ChangeCase", "options": "{}"}])
    step_rows = fetch_chain_steps(header["chain_id"])

    recorder = ChainExecutionRecorder(_FakeChain(header))
    recorder.record_step(1, _FakeStepPlugin(step_rows[0]), "a", "A")
    execution_id = recorder.finish("a", "A")

    delete_plugin_history_execution(execution_id)

    assert fetch_recent_plugin_history() == []
    assert fetch_execution_steps(execution_id) == []
