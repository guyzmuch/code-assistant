def register_plugin_classes(db_connection, plugin_classes):
    cursor = db_connection.cursor()

    for plugin_class in plugin_classes:
        cursor.execute(
            "SELECT * FROM plugins WHERE name = ?", (plugin_class.__name__,)
        )
        plugin_from_database = cursor.fetchone()
        # print(f"plugin_from_database: {plugin_from_database}")
        if not plugin_from_database:
            cursor.execute(
                """
                INSERT INTO plugins
                    (name, activated, new_plugin, options, shortcut, custom_name)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (plugin_class.__name__, 1, 1, "{}", "", ""),
            )
        db_connection.commit()
