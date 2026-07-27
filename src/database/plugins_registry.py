import uuid

from app.context import db_connection


def count_active_plugins():
    # Reuse the top-level query so counting and listing stay in sync (and use
    # the same "standalone or chain header" definition), never chain steps.
    return len(fetch_configured_plugins())


def fetch_configured_plugins():
    conn = db_connection()
    cursor = conn.cursor()
    # Top-level runnables: standalone plugins (no chain_id) and chain headers
    # (chain_position 0), never the individual chain steps (chain_position >= 1).
    cursor.execute(
        """
        SELECT * FROM plugins
        WHERE archived = 0
          AND (
                chain_id IS NULL
                OR (chain_id IS NOT NULL AND chain_position = 0)
              )
        ORDER BY id
        """
    )
    return cursor.fetchall()


def get_plugin_by_id(plugin_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plugins WHERE id = ?", (plugin_id,))
    return cursor.fetchone()


def archive_plugin(plugin_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE plugins SET archived = 1 WHERE id = ?",
        (plugin_id,),
    )
    conn.commit()


def _insert_plugin(
    cursor,
    *,
    name,
    custom_name="",
    options="{}",
    shortcut="",
    show_in_panel=True,
    chain_id=None,
    chain_position=None,
):
    """Insert one plugins row WITHOUT committing, returning its new id.

    Shared by create_plugin (single standalone row) and create_chain (a header
    plus several step rows) so both build rows the same way; the caller commits
    once when all its rows are inserted.
    """
    cursor.execute(
        """
        INSERT INTO plugins
            (name, custom_name, options, shortcut, config_version, archived,
             show_in_panel, chain_id, chain_position)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            custom_name,
            options,
            shortcut,
            1,
            0,
            int(show_in_panel),
            chain_id,
            chain_position,
        ),
    )
    return cursor.lastrowid


def create_plugin(name, custom_name="", options="{}", *, show_in_panel=True):
    conn = db_connection()
    cursor = conn.cursor()
    plugin_id = _insert_plugin(
        cursor,
        name=name,
        custom_name=custom_name,
        options=options,
        show_in_panel=show_in_panel,
    )
    conn.commit()
    return get_plugin_by_id(plugin_id)


def update_plugin(plugin_id, custom_name, options, *, show_in_panel=True):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE plugins
        SET custom_name = ?, options = ?, show_in_panel = ?,
            config_version = config_version + 1
        WHERE id = ?
        """,
        (custom_name, options, int(show_in_panel), plugin_id),
    )
    conn.commit()
    return get_plugin_by_id(plugin_id)


def get_chain_header(chain_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM plugins WHERE chain_id = ? AND chain_position = 0",
        (chain_id,),
    )
    return cursor.fetchone()


def fetch_chain_steps(chain_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM plugins
        WHERE chain_id = ? AND chain_position >= 1 AND archived = 0
        ORDER BY chain_position
        """,
        (chain_id,),
    )
    return cursor.fetchall()


def create_chain(custom_name, steps, *, show_in_panel=True):
    """Create a chain: one header row (position 0) plus ordered step rows.

    ``steps`` is a list of dicts like {"name": <plugin class>, "options": <json>}.
    """
    conn = db_connection()
    cursor = conn.cursor()
    chain_id = uuid.uuid4().hex
    # Header row: no plugin class/options of its own; holds the chain metadata.
    _insert_plugin(
        cursor,
        name=None,
        custom_name=custom_name,
        options=None,
        show_in_panel=show_in_panel,
        chain_id=chain_id,
        chain_position=0,
    )
    # Each step is a hidden plugin row (show_in_panel False) carrying its own
    # plugin class name and options.
    for position, step in enumerate(steps, start=1):
        _insert_plugin(
            cursor,
            name=step["name"],
            options=step.get("options", "{}"),
            show_in_panel=False,
            chain_id=chain_id,
            chain_position=position,
        )
    conn.commit()
    return get_chain_header(chain_id)


def update_chain(chain_id, custom_name, steps, *, show_in_panel=True):
    """Update a chain header and replace its steps in a single transaction.

    Old step rows are archived (not deleted) so existing history rows that
    reference them by plugin_id still resolve their plugin name.
    """
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE plugins
        SET custom_name = ?, show_in_panel = ?,
            config_version = config_version + 1
        WHERE chain_id = ? AND chain_position = 0
        """,
        (custom_name, int(show_in_panel), chain_id),
    )
    # Archive (do not delete) the current steps, then insert the new ones. The
    # archived rows are kept so old history rows referencing them by plugin_id
    # still resolve their plugin name; the partial unique index ignores archived
    # rows, so new steps can reuse the same positions.
    cursor.execute(
        """
        UPDATE plugins SET archived = 1
        WHERE chain_id = ? AND chain_position >= 1 AND archived = 0
        """,
        (chain_id,),
    )
    for position, step in enumerate(steps, start=1):
        _insert_plugin(
            cursor,
            name=step["name"],
            options=step.get("options", "{}"),
            show_in_panel=False,
            chain_id=chain_id,
            chain_position=position,
        )
    conn.commit()
    return get_chain_header(chain_id)


def archive_chain(chain_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE plugins SET archived = 1 WHERE chain_id = ?",
        (chain_id,),
    )
    conn.commit()
