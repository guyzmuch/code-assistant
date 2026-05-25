from tkinter import ttk

from app.constants import COPY_SYMBOL
from app.plugins_loader import load_plugins
from utils.plugins import plugin_entrance
from utils.ui import get_text_from_clipboard
from views.main_layout import MainLayout


def make_plugin_command(plugin, layout, db_connection, *, from_clipboard=False):
    def run():
        if from_clipboard:
            get_text_from_clipboard(layout.user_input_text_area)
        plugin_entrance(
            plugin,
            layout.user_input_text_area,
            layout.user_output_text_area,
            db_connection,
        )

    return run


def populate_plugin_buttons(layout: MainLayout, db_connection):
    plugins = load_plugins(db_connection)
    print("***** End of loading plugins: loaded ", len(plugins), " plugins")

    plugins_dict = {
        plugin_class.__name__: plugin_class for plugin_class in plugins
    }

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM plugins WHERE activated = 1")
    plugins_from_database = cursor.fetchall()

    row = 0
    for plugin_from_database in plugins_from_database:
        if plugin_from_database["name"] not in plugins_dict:
            print(
                "Plugin from database not found in plugins: ",
                plugin_from_database["name"],
            )
            continue

        plugin_instance = plugins_dict[plugin_from_database["name"]](
            custom_name=plugin_from_database["custom_name"],
            options=plugin_from_database["options"],
            shortcut=plugin_from_database["shortcut"],
        )

        print("Instanciated plugin: ", plugin_instance.get_name())

        # Set up the "from clipboard" button
        run_plugin_from_clipboard = make_plugin_command(
            plugin_instance, layout, db_connection, from_clipboard=True
        )

        plugin_from_clipboard_button = ttk.Button(
            layout.frame_buttons,
            text=COPY_SYMBOL,
            command=run_plugin_from_clipboard,
        )
        plugin_from_clipboard_button.grid(
            row=row, column=0, sticky="ew", padx=(5, 5)
        )
        plugin_from_clipboard_button.configure(width=2)

        # Set up the "from input" button
        run_plugin = make_plugin_command(
            plugin_instance, layout, db_connection
        )
        plugin_button = ttk.Button(
            layout.frame_buttons,
            text=plugin_instance.get_name(),
            command=run_plugin,
        )
        plugin_button.grid(row=row, column=1, sticky="ew", padx=(0, 5))
        plugin_button.configure(width=15)
        row += 1
