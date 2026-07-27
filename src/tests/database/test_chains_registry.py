from database.plugins_registry import (
    archive_chain,
    create_chain,
    fetch_chain_steps,
    fetch_configured_plugins,
    get_chain_header,
    update_chain,
)
from tests.database.conftest import memory_db


def _steps():
    return [
        {"name": "ReplaceText", "options": '{"search": "foo"}'},
        {"name": "ChangeCase", "options": '{"case": "uppercase"}'},
    ]


def test_create_chain_stores_header_and_ordered_steps():
    memory_db()
    header = create_chain("My chain", _steps(), show_in_panel=True)

    assert header["custom_name"] == "My chain"
    assert header["chain_position"] == 0
    assert header["config_version"] == 1
    assert header["show_in_panel"] == 1

    steps = fetch_chain_steps(header["chain_id"])
    assert [s["name"] for s in steps] == ["ReplaceText", "ChangeCase"]
    assert [s["chain_position"] for s in steps] == [1, 2]


def test_fetch_configured_plugins_returns_header_not_steps():
    memory_db()
    header = create_chain("My chain", _steps())

    rows = fetch_configured_plugins()
    assert len(rows) == 1
    assert rows[0]["chain_id"] == header["chain_id"]
    assert rows[0]["chain_position"] == 0


def test_update_chain_increments_version_and_replaces_steps():
    memory_db()
    header = create_chain("Chain", _steps())

    updated = update_chain(
        header["chain_id"],
        "Renamed",
        [{"name": "ChangeCase", "options": "{}"}],
        show_in_panel=False,
    )

    assert updated["custom_name"] == "Renamed"
    assert updated["config_version"] == 2
    assert updated["show_in_panel"] == 0

    steps = fetch_chain_steps(header["chain_id"])
    assert [s["name"] for s in steps] == ["ChangeCase"]
    assert [s["chain_position"] for s in steps] == [1]


def test_update_chain_archives_old_steps_but_keeps_them_resolvable():
    memory_db()
    header = create_chain("Chain", _steps())
    old_steps = fetch_chain_steps(header["chain_id"])
    old_step_id = old_steps[0]["id"]

    update_chain(
        header["chain_id"],
        "Chain",
        [{"name": "ChangeCase", "options": "{}"}],
    )

    # Old step row still exists (archived), so history referencing it resolves.
    from database.plugins_registry import get_plugin_by_id

    old_row = get_plugin_by_id(old_step_id)
    assert old_row is not None
    assert old_row["archived"] == 1


def test_archive_chain_hides_header_and_steps():
    memory_db()
    header = create_chain("Chain", _steps())

    archive_chain(header["chain_id"])

    assert fetch_configured_plugins() == []
    assert fetch_chain_steps(header["chain_id"]) == []
    assert get_chain_header(header["chain_id"])["archived"] == 1
