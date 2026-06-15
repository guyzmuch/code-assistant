def count_active_plugins(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM plugins WHERE archived = 0")
    return cursor.fetchone()[0]


def fetch_configured_plugins(db_connection):
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT * FROM plugins WHERE archived = 0 ORDER BY id"
    )
    return cursor.fetchall()


def get_plugin_by_id(db_connection, plugin_id):
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM plugins WHERE id = ?", (plugin_id,))
    return cursor.fetchone()


def archive_plugin(db_connection, plugin_id):
    cursor = db_connection.cursor()
    cursor.execute(
        "UPDATE plugins SET archived = 1 WHERE id = ?",
        (plugin_id,),
    )
    db_connection.commit()


def create_plugin(db_connection, name, custom_name="", options="{}"):
    cursor = db_connection.cursor()
    cursor.execute(
        """
        INSERT INTO plugins
            (name, custom_name, options, shortcut, config_version, archived)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, custom_name, options, "", 1, 0),
    )
    db_connection.commit()
    return get_plugin_by_id(db_connection, cursor.lastrowid)


def update_plugin(db_connection, plugin_id, custom_name, options):
    cursor = db_connection.cursor()
    cursor.execute(
        """
        UPDATE plugins
        SET custom_name = ?, options = ?, config_version = config_version + 1
        WHERE id = ?
        """,
        (custom_name, options, plugin_id),
    )
    db_connection.commit()
    return get_plugin_by_id(db_connection, plugin_id)
