from tkinter import ttk

from app.constants import COPY_SYMBOL
from app.plugins_loader import load_plugins
from utils.plugins import plugin_entrance
from utils.ui import get_text_from_clipboard
from views.main_layout import MainLayout


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

        plugin_from_clipboard_button = ttk.Button(
            layout.frame_buttons,
            text=f"{COPY_SYMBOL}",
            command=lambda p=plugin_instance: [
                get_text_from_clipboard(layout.user_input_text_area),
                plugin_entrance(
                    p,
                    layout.user_input_text_area,
                    layout.user_output_text_area,
                    db_connection,
                ),
            ],
        )
        plugin_from_clipboard_button.grid(
            row=row, column=0, sticky="ew", padx=(5, 5)
        )

        plugin_button = ttk.Button(
            layout.frame_buttons,
            text=plugin_instance.get_name(),
            command=lambda p=plugin_instance: plugin_entrance(
                p,
                layout.user_input_text_area,
                layout.user_output_text_area,
                db_connection,
            ),
        )
        plugin_button.grid(row=row, column=1, sticky="ew", padx=(0, 5))
        row += 1

        plugin_from_clipboard_button.configure(width=2)
        plugin_button.configure(width=15)
