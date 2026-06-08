import tkinter as tk
from tkinterdnd2 import DND_TEXT


def setup_text_drop_target(text_widget: tk.Text):
    """Accept text dragged from other apps; show insert cursor at drop position."""
    saved_insert = {"index": None}

    def index_at_pointer(event):
        bd = int(text_widget.cget("bd")) + int(
            text_widget.cget("highlightthickness")
        )
        x = event.x_root - text_widget.winfo_rootx() - bd
        y = event.y_root - text_widget.winfo_rooty() - bd
        return text_widget.index(f"@{x},{y}")

    def on_drop_enter(event):
        text_widget.focus_force()
        saved_insert["index"] = text_widget.index("insert")
        return event.action

    def on_drop_position(event):
        index = index_at_pointer(event)
        text_widget.mark_set("insert", index)
        text_widget.see(index)
        return event.action

    def on_drop_leave(event):
        if saved_insert["index"] is not None:
            text_widget.mark_set("insert", saved_insert["index"])
            saved_insert["index"] = None
        return event.action

    def on_drop(event):
        if event.data:
            index = index_at_pointer(event)
            text_widget.insert(index, event.data)
        saved_insert["index"] = None
        return event.action

    text_widget.drop_target_register(DND_TEXT)
    text_widget.dnd_bind("<<DropEnter>>", on_drop_enter)
    text_widget.dnd_bind("<<DropPosition>>", on_drop_position)
    text_widget.dnd_bind("<<DropLeave>>", on_drop_leave)
    text_widget.dnd_bind("<<Drop>>", on_drop)
