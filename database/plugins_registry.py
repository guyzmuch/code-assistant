from app.context import db_connection


def count_active_plugins():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM plugins WHERE archived = 0")
    return cursor.fetchone()[0]


def fetch_configured_plugins():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM plugins WHERE archived = 0 ORDER BY id"
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


def create_plugin(name, custom_name="", options="{}"):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO plugins
            (name, custom_name, options, shortcut, config_version, archived)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, custom_name, options, "", 1, 0),
    )
    conn.commit()
    return get_plugin_by_id(cursor.lastrowid)


def update_plugin(plugin_id, custom_name, options):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE plugins
        SET custom_name = ?, options = ?, config_version = config_version + 1
        WHERE id = ?
        """,
        (custom_name, options, plugin_id),
    )
    conn.commit()
    return get_plugin_by_id(plugin_id)
