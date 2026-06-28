import sys
import tkinter as tk
from tkinter import messagebox

from app.version import __version__
from app.window import WINDOW_TITLE


def _bind_accelerators(root, bindings):
    for sequence, callback in bindings.items():
        root.bind_all(sequence, lambda e, cb=callback: cb(), add="+")


def create_app_menu(root, *, on_quit, on_history, on_settings) -> tk.Menu:
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
    messagebox.showinfo(
        WINDOW_TITLE,
        f"{WINDOW_TITLE} {__version__}\n\nSmall developer utilities for text and data.",
        parent=root,
    )
