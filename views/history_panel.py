import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk

from app.actions import paste_text_to_input
from database.plugin_history import fetch_recent_plugin_history, history_row_title
DETAIL_TEXT_HEIGHT = 7


class HistoryPanel(ttk.Frame):
    def __init__(self, parent, db_connection, input_text_area, **kwargs):
        super().__init__(parent, **kwargs)
        self._db_connection = db_connection
        self._input_text_area = input_text_area
        self._rows = []
        self._expanded_row = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._canvas.yview
        )
        self._scroll_frame = ttk.Frame(self._canvas)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            ),
        )
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._scroll_frame, anchor="nw"
        )
        self._canvas.configure(yscrollcommand=scrollbar.set)

        def _on_canvas_configure(event):
            self._canvas.itemconfig(
                self._canvas_window, width=event.width
            )

        self._canvas.bind("<Configure>", _on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Button-4>", self._on_mousewheel_linux)
        self._canvas.bind("<Button-5>", self._on_mousewheel_linux)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        delta = -1 if event.num == 4 else 1
        self._canvas.yview_scroll(delta, "units")

    def refresh(self):
        for child in self._scroll_frame.winfo_children():
            child.destroy()
        self._rows.clear()
        self._expanded_row = None

        records = fetch_recent_plugin_history(self._db_connection)
        if not records:
            ttk.Label(self._scroll_frame, text="No history yet").pack(
                anchor="w", padx=5, pady=5
            )
            return

        for record in records:
            self._add_row(record)

    def _add_row(self, record):
        row_frame = ttk.Frame(self._scroll_frame)
        row_frame.pack(fill=tk.X, padx=5, pady=2)

        title = history_row_title(record)
        header = ttk.Button(
            row_frame,
            text=title,
            command=lambda r=record: self._toggle_row(r),
        )
        header.pack(fill=tk.X)

        body = ttk.Frame(row_frame)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.columnconfigure(2, weight=1)

        input_text = scrolledtext.ScrolledText(
            body, height=DETAIL_TEXT_HEIGHT, wrap=tk.WORD, state=tk.DISABLED
        )
        input_text.configure(state=tk.NORMAL)
        input_text.insert("1.0", record["input"] or "")
        input_text.configure(state=tk.DISABLED)

        separator = ttk.Label(body, text=">", padding=5)

        output_text = scrolledtext.ScrolledText(
            body, height=DETAIL_TEXT_HEIGHT, wrap=tk.WORD, state=tk.DISABLED
        )
        output_text.configure(state=tk.NORMAL)
        output_text.insert("1.0", record["output"] or "")
        output_text.configure(state=tk.DISABLED)

        input_text.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        separator.grid(row=0, column=1, sticky="ns")
        output_text.grid(row=0, column=2, sticky="nsew", padx=(2, 0))

        buttons_row = ttk.Frame(body)
        ttk.Button(
            buttons_row,
            text="Paste to input",
            command=lambda t=record["input"] or "": paste_text_to_input(
                self._input_text_area, t
            ),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(
            buttons_row,
            text="Paste to input",
            command=lambda t=record["output"] or "": paste_text_to_input(
                self._input_text_area, t
            ),
        ).grid(row=0, column=2, sticky="ew", padx=(2, 0))
        buttons_row.columnconfigure(0, weight=1)
        buttons_row.columnconfigure(2, weight=1)
        buttons_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 0))

        row_data = {
            "record": record,
            "frame": row_frame,
            "header": header,
            "body": body,
        }
        self._rows.append(row_data)

    def _toggle_row(self, record):
        for row in self._rows:
            if row["record"]["id"] == record["id"]:
                if row["body"].winfo_ismapped():
                    row["body"].pack_forget()
                    self._expanded_row = None
                else:
                    if self._expanded_row is not None:
                        self._expanded_row["body"].pack_forget()
                    row["body"].pack(fill=tk.X, pady=(4, 0))
                    self._expanded_row = row
                return
