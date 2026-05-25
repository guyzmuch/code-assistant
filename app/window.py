import tkinter as tk

WINDOW_TITLE = "Dev assistant"
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 650


def create_root_window():
    root = tk.Tk()
    root.title(WINDOW_TITLE)

    screen_width = root.winfo_screenwidth()
    root.geometry(
        f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{screen_width - WINDOW_WIDTH}+0"
    )

    return root
