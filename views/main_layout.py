import tkinter as tk
from dataclasses import dataclass

import pyperclip
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk

from app.actions import copy_result_to_input
from app.constants import COPY_SYMBOL


@dataclass
class MainLayout:
    main_container: ttk.Frame
    frame_buttons: ttk.Frame
    frame_output_buttons: ttk.Frame
    user_input_text_area: scrolledtext.ScrolledText
    user_output_text_area: scrolledtext.ScrolledText


def create_main_layout(root) -> MainLayout:
    main_container = ttk.Frame(root)
    main_container["padding"] = 10
    main_container.pack(side="top", fill="both", expand=True)

    main_container.columnconfigure(0, weight=3)
    main_container.columnconfigure(1, weight=2)
    main_container.columnconfigure(2, weight=3)

    main_container.rowconfigure(0, weight=10)
    main_container.rowconfigure(1, weight=1)
    main_container.rowconfigure(2, weight=1)

    frame_buttons = ttk.Frame(main_container)
    frame_buttons.columnconfigure(0, weight=1)
    frame_buttons.columnconfigure(1, weight=10)

    frame_output_buttons = ttk.Frame(main_container)
    frame_output_buttons["padding"] = 5

    user_input_text_area = scrolledtext.ScrolledText(
        main_container,
        height=35,
        width=30,
        wrap=tk.NONE,
    )

    user_output_text_area = scrolledtext.ScrolledText(
        main_container,
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
    frame_buttons.grid(row=0, column=1, sticky="nsew")
    user_output_text_area.grid(row=0, column=2, sticky="nsew")
    frame_output_buttons.grid(row=1, column=2, sticky="nsew")

    return MainLayout(
        main_container=main_container,
        frame_buttons=frame_buttons,
        frame_output_buttons=frame_output_buttons,
        user_input_text_area=user_input_text_area,
        user_output_text_area=user_output_text_area,
    )
