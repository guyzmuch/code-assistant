import tkinter as tk
from tkinter import ttk

from app.branding import WINDOW_TITLE, app_icon_path
from app.version import __version__


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(f"About {WINDOW_TITLE}")
        self.transient(parent)
        self.resizable(False, False)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        icon_path = app_icon_path()
        if icon_path is not None:
            icon_image = tk.PhotoImage(file=str(icon_path))
            icon_label = ttk.Label(frame, image=icon_image)
            icon_label.image = icon_image
            icon_label.pack(pady=(0, 12))

        ttk.Label(frame, text=WINDOW_TITLE, font=("", 14, "bold")).pack()
        ttk.Label(frame, text=f"Version {__version__}").pack(pady=(4, 12))
        ttk.Label(
            frame,
            text="Small developer utilities for text and data.",
            justify="center",
        ).pack()

        ttk.Button(frame, text="Close", command=self.destroy).pack(pady=(16, 0))

        self.bind("<Escape>", lambda _event: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent_x + (parent_w - width) // 2
        y = parent_y + (parent_h - height) // 2
        self.geometry(f"+{x}+{y}")
