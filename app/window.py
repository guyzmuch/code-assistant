import tkinter as tk

WINDOW_TITLE = "Dev assistant"
WINDOW_HEIGHT = 650
COMPACT_WINDOW_WIDTH = 700
PLUGIN_PANEL_WIDTH = 200
DEFAULT_HISTORY_SASH_WIDTH = 320


def screen_width(root) -> int:
    return root.winfo_screenwidth()


def create_root_window():
    root = tk.Tk()
    root.title(WINDOW_TITLE)

    x = screen_width(root) - COMPACT_WINDOW_WIDTH
    root.geometry(f"{COMPACT_WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+0")

    return root


def set_window_full_width(root):
    root.update_idletasks()
    width = screen_width(root)
    height = root.winfo_height()
    root.geometry(f"{width}x{height}+0+0")


def set_window_compact_top_right(root):
    root.update_idletasks()
    width = COMPACT_WINDOW_WIDTH
    height = root.winfo_height()
    x = screen_width(root) - width
    root.geometry(f"{width}x{height}+{x}+0")
