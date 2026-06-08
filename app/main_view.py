import tkinter as tk
from tkinter import ttk

from app.menu import create_app_menu
from app.plugin_panel import populate_plugin_buttons
from app.window import (
    COMPACT_WINDOW_WIDTH,
    set_window_compact_top_right,
    set_window_full_width,
)
from views.history_panel import HistoryPanel
from views.main_layout import create_main_layout, set_initial_main_sash_positions


def create_main_view(root, db_connection):
    history_visible = {"value": False}

    body_frame = ttk.Frame(root)
    body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    outer_paned = ttk.Panedwindow(body_frame, orient=tk.HORIZONTAL)
    outer_paned.pack(fill=tk.BOTH, expand=True)

    main_wrapper = ttk.Frame(outer_paned, width=COMPACT_WINDOW_WIDTH)
    main_wrapper.pack_propagate(False)
    main_paned = ttk.Panedwindow(main_wrapper, orient=tk.HORIZONTAL)
    main_paned.pack(fill=tk.BOTH, expand=True)
    outer_paned.add(main_wrapper, weight=0)

    layout = create_main_layout(main_paned)
    history_panel = HistoryPanel(
        outer_paned, db_connection, layout.user_input_text_area
    )

    def toggle_history():
        if history_visible["value"]:
            outer_paned.forget(history_panel)
            set_window_compact_top_right(root)
            history_visible["value"] = False
        else:
            outer_paned.insert(0, history_panel, weight=1)
            set_window_full_width(root)
            root.update_idletasks()
            history_panel.refresh()
            history_visible["value"] = True

    create_app_menu(root, on_quit=root.destroy, on_history=toggle_history)
    populate_plugin_buttons(layout, db_connection)

    root.update_idletasks()
    set_initial_main_sash_positions(main_paned)
