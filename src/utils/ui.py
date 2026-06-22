import tkinter as tk


def _read_clipboard(widget) -> str:
    """Read clipboard via Tk (avoids pyperclip/xsel hangs on Linux)."""
    try:
        return widget.clipboard_get()
    except tk.TclError:
        return ""


def write_to_clipboard(widget, text: str) -> None:
    widget.clipboard_clear()
    widget.clipboard_append(text)


def get_text_from_clipboard(input_text_area):
    input_text_area.delete("1.0", tk.END)
    input_text_area.insert("1.0", _read_clipboard(input_text_area))


def split_lines(input_text_area):
    user_input = input_text_area.get("1.0", "end-1c")
    return user_input.split("\n")
