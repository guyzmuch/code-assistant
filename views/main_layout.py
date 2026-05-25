import tkinter as tk
from dataclasses import dataclass

import pyperclip
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk

from app.actions import copy_result_to_input
from app.constants import COPY_SYMBOL
from app.window import PLUGIN_PANEL_WIDTH


@dataclass
class MainLayout:
    main_paned: ttk.Panedwindow
    frame_input: ttk.Frame
    frame_buttons: ttk.Frame
    frame_output: ttk.Frame
    frame_output_buttons: ttk.Frame
    user_input_text_area: scrolledtext.ScrolledText
    user_output_text_area: scrolledtext.ScrolledText


def create_main_layout(paned_parent: ttk.Panedwindow) -> MainLayout:
    frame_input = ttk.Frame(paned_parent, padding=10)
    frame_buttons = ttk.Frame(
        paned_parent, width=PLUGIN_PANEL_WIDTH, padding=(0, 10)
    )
    frame_buttons.grid_propagate(False)
    frame_output = ttk.Frame(paned_parent, padding=10)

    paned_parent.add(frame_input, weight=1)
    paned_parent.add(frame_buttons, weight=0)
    paned_parent.add(frame_output, weight=1)

    frame_input.rowconfigure(0, weight=1)
    frame_input.columnconfigure(0, weight=1)
    frame_buttons.columnconfigure(0, weight=0)
    frame_buttons.columnconfigure(1, weight=1)
    frame_output.rowconfigure(0, weight=1)
    frame_output.rowconfigure(1, weight=0)
    frame_output.columnconfigure(0, weight=1)

    frame_output_buttons = ttk.Frame(frame_output)
    frame_output_buttons["padding"] = 5

    user_input_text_area = scrolledtext.ScrolledText(
        frame_input,
        height=35,
        width=30,
        wrap=tk.NONE,
    )

    user_output_text_area = scrolledtext.ScrolledText(
        frame_output,
        height=35,
        width=30,
        wrap=tk.NONE,
    )

    copy_result_to_input_button = ttk.Button(
        frame_output_buttons,
        text="⤾ result to input",
        command=lambda: copy_result_to_input(
            user_input_text_area, user_output_text_area
        ),
    )
    copy_result_to_clipboard_button = ttk.Button(
        frame_output_buttons,
        text=f"{COPY_SYMBOL} clipboard",
        command=lambda: pyperclip.copy(
            user_output_text_area.get("1.0", "end-1c")
        ),
    )
    copy_result_to_input_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    copy_result_to_clipboard_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

    user_input_text_area.grid(row=0, column=0, sticky="nsew")
    user_output_text_area.grid(row=0, column=0, sticky="nsew")
    frame_output_buttons.grid(row=1, column=0, sticky="ew")

    return MainLayout(
        main_paned=paned_parent,
        frame_input=frame_input,
        frame_buttons=frame_buttons,
        frame_output=frame_output,
        frame_output_buttons=frame_output_buttons,
        user_input_text_area=user_input_text_area,
        user_output_text_area=user_output_text_area,
    )


def set_initial_main_sash_positions(main_paned: ttk.Panedwindow):
    """Place plugin column at PLUGIN_PANEL_WIDTH; input/output share the rest."""
    main_paned.update_idletasks()
    width = main_paned.winfo_width()
    if width <= 1:
        return
    remaining = width - PLUGIN_PANEL_WIDTH
    input_width = remaining // 2
    main_paned.sashpos(0, input_width)
    main_paned.sashpos(1, input_width + PLUGIN_PANEL_WIDTH)
