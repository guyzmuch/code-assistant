import tkinter as tk
from dataclasses import dataclass, field

import pyperclip
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk

from app.actions import copy_result_to_input
from app.constants import (
    COLLAPSE_OUTPUT_SYMBOL,
    COPY_SYMBOL,
    EXPAND_OUTPUT_SYMBOL,
)
from app.window import PLUGIN_PANEL_WIDTH
from utils.text_drop import setup_text_drop_target


@dataclass
class MainLayout:
    main_paned: ttk.Panedwindow
    frame_input: ttk.Frame
    frame_buttons: ttk.Frame
    frame_output: ttk.Frame
    frame_output_buttons: ttk.Frame
    user_input_text_area: scrolledtext.ScrolledText
    user_output_text_area: scrolledtext.ScrolledText
    output_overlay: ttk.Frame
    output_overlay_text_area: scrolledtext.ScrolledText
    _output_overlay_visible: bool = field(default=False, repr=False)

    def show_output_overlay(self):
        self._sync_overlay_from_output()
        self.output_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.output_overlay.lift()
        self._output_overlay_visible = True

    def hide_output_overlay(self):
        self._sync_output_from_overlay()
        self.output_overlay.place_forget()
        self._output_overlay_visible = False

    def set_output_text(self, text: str):
        self.user_output_text_area.delete("1.0", tk.END)
        self.user_output_text_area.insert("1.0", text)
        if self._output_overlay_visible:
            self.output_overlay_text_area.delete("1.0", tk.END)
            self.output_overlay_text_area.insert("1.0", text)

    def _sync_overlay_from_output(self):
        text = self.user_output_text_area.get("1.0", "end-1c")
        self.output_overlay_text_area.delete("1.0", tk.END)
        self.output_overlay_text_area.insert("1.0", text)

    def _sync_output_from_overlay(self):
        text = self.output_overlay_text_area.get("1.0", "end-1c")
        self.user_output_text_area.delete("1.0", tk.END)
        self.user_output_text_area.insert("1.0", text)


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

    frame_output_content = ttk.Frame(frame_output)
    frame_output_content.grid(row=0, column=0, sticky="nsew")
    frame_output_content.rowconfigure(0, weight=1)
    frame_output_content.columnconfigure(0, weight=1)

    frame_output_buttons = ttk.Frame(frame_output)
    frame_output_buttons["padding"] = 5

    user_input_text_area = scrolledtext.ScrolledText(
        frame_input,
        height=35,
        width=30,
        wrap=tk.NONE,
    )

    user_output_text_area = scrolledtext.ScrolledText(
        frame_output_content,
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

    setup_text_drop_target(user_input_text_area)
    user_input_text_area.grid(row=0, column=0, sticky="nsew")
    user_output_text_area.grid(row=0, column=0, sticky="nsew")
    frame_output_buttons.grid(row=1, column=0, sticky="ew")

    output_overlay = ttk.Frame(paned_parent, padding=10)
    output_overlay_text_area = scrolledtext.ScrolledText(
        output_overlay,
        height=35,
        width=30,
        wrap=tk.NONE,
    )

    layout = MainLayout(
        main_paned=paned_parent,
        frame_input=frame_input,
        frame_buttons=frame_buttons,
        frame_output=frame_output,
        frame_output_buttons=frame_output_buttons,
        user_input_text_area=user_input_text_area,
        user_output_text_area=user_output_text_area,
        output_overlay=output_overlay,
        output_overlay_text_area=output_overlay_text_area,
    )
    _setup_output_overlay(layout, frame_output_content)
    return layout


def _setup_output_overlay(layout: MainLayout, frame_output_content: ttk.Frame):
    overlay = layout.output_overlay
    overlay_text = layout.output_overlay_text_area

    overlay.rowconfigure(0, weight=1)
    overlay.columnconfigure(0, weight=1)

    overlay_text.grid(row=0, column=0, sticky="nsew")

    expand_button = ttk.Button(
        frame_output_content,
        text=EXPAND_OUTPUT_SYMBOL,
        width=3,
        command=layout.show_output_overlay,
    )
    expand_button.place(
        in_=layout.user_output_text_area,
        relx=1.0,
        rely=0.0,
        anchor="ne",
        x=-22,
        y=4,
    )

    collapse_button = ttk.Button(
        overlay,
        text=COLLAPSE_OUTPUT_SYMBOL,
        width=3,
        command=layout.hide_output_overlay,
    )
    collapse_button.place(
        in_=overlay_text,
        relx=1.0,
        rely=0.0,
        anchor="ne",
        x=-22,
        y=4,
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
