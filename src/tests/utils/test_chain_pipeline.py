from database.plugin_history import (
    HistoryRecorder,
    fetch_execution_steps,
    fetch_recent_plugin_history,
    is_chain_history_row,
)
from database.plugins_registry import create_chain, create_plugin
from tests.database.conftest import memory_db
from utils.plugins import load_runnable


def _make_chain():
    return create_chain(
        "Clean & Join",
        [
            {"name": "ChangeCase", "options": '{"case": "uppercase"}'},
            {"name": "JoinBySeparator", "options": '{"separator": "-"}'},
        ],
    )


def test_chain_execution_pipes_and_produces_final_output():
    memory_db()
    header = _make_chain()

    runnable = load_runnable(header)
    output = runnable.execute(["ab", "cd"], HistoryRecorder())

    assert output == ["AB-CD"]


def test_chain_execution_writes_grouped_history():
    memory_db()
    header = _make_chain()

    load_runnable(header).execute(["ab", "cd"], HistoryRecorder())

    top = fetch_recent_plugin_history()
    assert len(top) == 1
    summary = top[0]
    assert is_chain_history_row(summary)
    assert summary["input"] == "ab\ncd"
    assert summary["output"] == "AB-CD"

    steps = fetch_execution_steps(summary["execution_id"])
    assert [s["execution_position"] for s in steps] == [1, 2]
    assert steps[0]["input"] == "ab\ncd"
    assert steps[0]["output"] == "AB\nCD"
    assert steps[1]["input"] == "AB\nCD"
    assert steps[1]["output"] == "AB-CD"


def test_standalone_execution_is_not_a_chain_row():
    memory_db()
    plugin_row = create_plugin("ChangeCase", "Upper", '{"case": "uppercase"}')

    load_runnable(plugin_row).execute(["ab"], HistoryRecorder())

    top = fetch_recent_plugin_history()
    assert len(top) == 1
    assert is_chain_history_row(top[0]) is False
    assert top[0]["output"] == "AB"
