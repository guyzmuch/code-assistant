import sys
import tkinter as tk

from app.branding import WINDOW_TITLE
from app.plugin_panel import make_plugin_command
from app.plugins_loader import discover_plugin_classes
from app.recent_plugins import RecentPluginEntry, get_recent_plugins
from database.plugins_registry import fetch_configured_plugins, get_plugin_by_id
from utils.plugins import load_runnable
from views.about_dialog import AboutDialog

_plugins_menu = None


def _runnable_from_recent_entry(entry: RecentPluginEntry, plugins_by_name):
    if entry.plugin_id is not None:
        plugin_row = get_plugin_by_id(entry.plugin_id)
        if plugin_row is None or plugin_row["archived"]:
            return None
        return load_runnable(plugin_row, plugins_by_name)

    plugin_class = plugins_by_name.get(entry.plugin_name)
    if plugin_class is None:
        return None
    return plugin_class()


def populate_plugins_menu():
    if _plugins_menu is None:
        return

    _plugins_menu.delete(0, tk.END)

    plugin_classes = discover_plugin_classes()
    plugins_by_name = {
        plugin_class.__name__: plugin_class for plugin_class in plugin_classes
    }

    recent_menu = tk.Menu(_plugins_menu, tearoff=0)
    for entry in get_recent_plugins():
        runnable = _runnable_from_recent_entry(entry, plugins_by_name)
        if runnable is None:
            continue
        recent_menu.add_command(
            label=runnable.get_name(),
            command=make_plugin_command(runnable),
        )
    _plugins_menu.add_cascade(label="Recent", menu=recent_menu)

    favorites_menu = tk.Menu(_plugins_menu, tearoff=0)
    for row in fetch_configured_plugins():
        if row["show_in_panel"]:
            continue
        runnable = load_runnable(row, plugins_by_name)
        if runnable is None:
            continue
        favorites_menu.add_command(
            label=runnable.get_name(),
            command=make_plugin_command(runnable),
        )
    _plugins_menu.add_cascade(label="Favorites", menu=favorites_menu)
    _plugins_menu.add_separator()

    for plugin_class in sorted(
        plugin_classes, key=lambda cls: cls.DEFAULT_NAME.lower()
    ):
        plugin_instance = plugin_class()
        _plugins_menu.add_command(
            label=plugin_class.DEFAULT_NAME,
            command=make_plugin_command(plugin_instance),
        )


def repopulate_plugins_menu():
    populate_plugins_menu()


def _bind_accelerators(root, bindings):
    for sequence, callback in bindings.items():
        root.bind_all(sequence, lambda e, cb=callback: cb(), add="+")


def create_app_menu(root, *, on_quit, on_history, on_settings) -> tk.Menu:
    global _plugins_menu
    menubar = tk.Menu(root)
    is_macos = sys.platform == "darwin"
    mod = "Cmd" if is_macos else "Ctrl"

    if is_macos:
        app_menu = tk.Menu(menubar, name="apple", tearoff=0)
        menubar.add_cascade(menu=app_menu)
        app_menu.add_command(
            label=f"About {WINDOW_TITLE}",
            command=lambda: _show_about(root),
        )
        app_menu.add_separator()
        app_menu.add_command(
            label=f"Quit {WINDOW_TITLE}",
            command=on_quit,
            accelerator="Cmd+Q",
        )
        root.createcommand("tk::mac::Quit", on_quit)
    else:
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Quit",
            command=on_quit,
            accelerator=f"{mod}+Q",
        )
        menubar.add_cascade(label="File", menu=file_menu)

    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_command(
        label="Toggle History Panel",
        command=on_history,
        accelerator=f"{mod}+Shift+H",
    )
    menubar.add_cascade(label="View", menu=view_menu)

    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label="Settings…", command=on_settings)
    menubar.add_cascade(label="Settings", menu=settings_menu)

    _plugins_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Plugins", menu=_plugins_menu)
    populate_plugins_menu()

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(
        label=f"About {WINDOW_TITLE}",
        command=lambda: _show_about(root),
    )
    menubar.add_cascade(label="Help", menu=help_menu)

    root.config(menu=menubar)

    if is_macos:
        _bind_accelerators(
            root,
            {
                "<Command-Shift-H>": on_history,
                "<Command-Shift-h>": on_history,
            },
        )
    else:
        _bind_accelerators(
            root,
            {
                "<Control-Shift-H>": on_history,
                "<Control-Shift-h>": on_history,
                "<Control-q>": on_quit,
                "<Control-Q>": on_quit,
            },
        )

    return menubar


def _show_about(root):
    AboutDialog(root)
