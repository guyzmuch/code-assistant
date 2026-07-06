from tkinter import ttk

from app.constants import COPY_SYMBOL
from app.context import get
from app.plugins_loader import load_plugins
from database.plugins_registry import fetch_configured_plugins
from utils.plugins import plugin_entrance
from utils.ui import get_text_from_clipboard


def make_plugin_command(plugin, *, from_clipboard=False):
    def run():
        if from_clipboard:
            get_text_from_clipboard(get().layout.user_input_text_area)
        plugin_entrance(plugin)

    return run


def clear_plugin_buttons():
    layout = get().layout
    for child in layout.frame_buttons.winfo_children():
        child.destroy()


def populate_plugin_buttons():
    ctx = get()
    layout = ctx.layout

    plugins = load_plugins()
    print("***** End of loading plugins: loaded ", len(plugins), " plugins")

    plugins_dict = {
        plugin_class.__name__: plugin_class for plugin_class in plugins
    }

    plugins_from_database = fetch_configured_plugins()

    row = 0
    for plugin_from_database in plugins_from_database:
        if not plugin_from_database["show_in_panel"]:
            continue

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
            id=plugin_from_database["id"],
            config_version=plugin_from_database["config_version"],
        )

        print("Instanciated plugin: ", plugin_instance.get_name())

        run_plugin_from_clipboard = make_plugin_command(
            plugin_instance, from_clipboard=True
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

        run_plugin = make_plugin_command(plugin_instance)
        plugin_button = ttk.Button(
            layout.frame_buttons,
            text=plugin_instance.get_name(),
            command=run_plugin,
        )
        plugin_button.grid(row=row, column=1, sticky="ew", padx=(0, 5))
        plugin_button.configure(width=15)
        row += 1


def repopulate_plugin_buttons():
    clear_plugin_buttons()
    populate_plugin_buttons()
