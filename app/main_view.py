import tkinter as tk
from tkinter import ttk

from app.config import load_app_config
from app.context import init as init_app_context
from app.menu import create_app_menu
from app.plugin_panel import populate_plugin_buttons
from app.plugins_loader import ensure_default_plugins
from app.window import (
    COMPACT_WINDOW_WIDTH,
    set_window_compact_top_right,
    set_window_full_width,
)
from views.history_panel import HistoryPanel
from views.main_layout import (
    apply_text_font_size,
    create_main_layout,
    set_initial_main_sash_positions,
)
from views.settings_window import open_settings_window


def create_main_view(root, db_connection):
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
        outer_paned, layout.user_input_text_area
    )
    ctx = init_app_context(db_connection, layout, history_panel)

    app_config = load_app_config()
    apply_text_font_size(layout, app_config["text_font_size"])

    def toggle_history():
        if ctx.history_visible:
            outer_paned.forget(history_panel)
            set_window_compact_top_right(root)
            ctx.history_visible = False
        else:
            outer_paned.insert(0, history_panel, weight=1)
            set_window_full_width(root)
            root.update_idletasks()
            history_panel.refresh()
            ctx.history_visible = True

    create_app_menu(
        root,
        on_quit=root.destroy,
        on_history=toggle_history,
        on_settings=lambda: open_settings_window(root),
    )

    ensure_default_plugins(db_connection)
    populate_plugin_buttons()

    if app_config["history_open_at_startup"]:
        outer_paned.insert(0, history_panel, weight=1)
        set_window_full_width(root)
        ctx.history_visible = True
        history_panel.refresh()

    root.update_idletasks()
    set_initial_main_sash_positions(main_paned)
