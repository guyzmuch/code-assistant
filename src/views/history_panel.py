import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from app.actions import paste_text_to_input
from database.plugin_history import (
    count_execution_steps,
    delete_plugin_history_entry,
    delete_plugin_history_execution,
    fetch_execution_steps,
    fetch_recent_plugin_history,
    history_row_title,
    is_chain_history_row,
)
from database.plugin_history import _history_label as history_step_label
from views.history_step_details import HistoryStepDetailsWindow

HISTORY_ENTRY_LIMIT = 10
DETAIL_MIN_LINES = 7

HEADER_BG = "#f4f4f5"
HEADER_BG_ACTIVE = "#e4e4e7"
HEADER_BG_HOVER = "#ececef"
DETAIL_BG = "#fafafa"
SEPARATOR_FG = "#a1a1aa"

COLLAPSED_INDICATOR = "▶"
EXPANDED_INDICATOR = "▼"


class HistoryPanel(ttk.Frame):
    def __init__(self, parent, input_text_area, **kwargs):
        super().__init__(parent, **kwargs)
        self._input_text_area = input_text_area
        self._rows = []
        self._expanded_record_id = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, highlightthickness=0, bg=HEADER_BG)
        self._scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._canvas.yview
        )
        self._list_frame = tk.Frame(self._canvas, bg=HEADER_BG)
        self._list_window = self._canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw"
        )

        self._list_frame.bind("<Configure>", self._on_list_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Button-4>", self._on_mousewheel_linux)
        self._canvas.bind("<Button-5>", self._on_mousewheel_linux)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._scrollbar.grid(row=0, column=1, sticky="ns")

        self._detail_frame = self._create_detail_frame(self._list_frame)

    def _create_detail_frame(self, parent):
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)

        detail_input = self._create_readonly_text(frame)
        # Middle column matches the text-area row height (sticky ns) and gets its
        # width from packed content — place() would collapse the width to ~0.
        # The "(N)" count is only packed for chain runs.
        separator = tk.Frame(frame, bg=DETAIL_BG)
        sep_content = tk.Frame(separator, bg=DETAIL_BG)
        sep_content.pack(expand=True)
        steps_count = tk.Label(
            sep_content,
            text="",
            fg="#52525b",
            bg=DETAIL_BG,
            font=tkfont.Font(size=9),
        )
        arrow = tk.Label(
            sep_content,
            text="›",
            fg=SEPARATOR_FG,
            bg=DETAIL_BG,
            font=tkfont.Font(size=14),
        )
        arrow.pack()
        detail_output = self._create_readonly_text(frame)
        detail_input["container"].grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        separator.grid(row=0, column=1, sticky="ns", padx=4)
        detail_output["container"].grid(row=0, column=2, sticky="nsew", padx=(2, 0))

        self._bind_tooltip(steps_count)

        # Chain-only; full width, above the paste buttons.
        show_steps_btn = ttk.Button(frame, text="Show step details")
        show_steps_btn.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        show_steps_btn.grid_remove()

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        paste_input_btn = ttk.Button(buttons, text="Paste to input")
        paste_output_btn = ttk.Button(buttons, text="Paste to input")
        paste_input_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        paste_output_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        return {
            "frame": frame,
            "input": detail_input,
            "output": detail_output,
            "paste_input_btn": paste_input_btn,
            "paste_output_btn": paste_output_btn,
            "show_steps_btn": show_steps_btn,
            "steps_count": steps_count,
            "arrow": arrow,
        }

    def _create_readonly_text(self, parent):
        container = ttk.Frame(parent)
        text = tk.Text(
            container,
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d4d4d8",
            highlightcolor="#d4d4d8",
            bg=DETAIL_BG,
            fg="#18181b",
            padx=8,
            pady=8,
            height=DETAIL_MIN_LINES,
            cursor="arrow",
        )
        scrollbar = ttk.Scrollbar(
            container, orient=tk.VERTICAL, command=text.yview
        )
        text.configure(yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return {"container": container, "widget": text}

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._list_window, width=event.width)
        self._sync_list_frame_height(event.height)

    def _on_list_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._sync_list_frame_height(self._canvas.winfo_height())

    def _sync_list_frame_height(self, viewport_height):
        if viewport_height <= 1:
            return
        content_height = self._list_frame.winfo_reqheight()
        frame_height = max(viewport_height, content_height)
        self._canvas.itemconfig(self._list_window, height=frame_height)

    def _on_mousewheel(self, event):
        if self._canvas.winfo_height() < self._list_frame.winfo_reqheight():
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if self._canvas.winfo_height() < self._list_frame.winfo_reqheight():
            delta = -1 if event.num == 4 else 1
            self._canvas.yview_scroll(delta, "units")

    def refresh(self):
        for child in self._list_frame.winfo_children():
            if child is not self._detail_frame["frame"]:
                child.destroy()
        self._rows.clear()
        self._expanded_record_id = None
        self._detail_frame["frame"].pack_forget()
        self._set_readonly_text(self._detail_frame["input"]["widget"], "")
        self._set_readonly_text(self._detail_frame["output"]["widget"], "")
        self._reset_chain_summary()

        records = fetch_recent_plugin_history(limit=HISTORY_ENTRY_LIMIT)
        if not records:
            tk.Label(
                self._list_frame,
                text="No history yet",
                bg=HEADER_BG,
                fg="#71717a",
                anchor="w",
                padx=12,
                pady=10,
            ).pack(fill=tk.X)
            return

        for index, record in enumerate(records):
            self._add_header_row(record, is_last=index == len(records) - 1)

        self._expand_row(records[0])

    def _add_header_row(self, record, *, is_last):
        title = history_row_title(record)
        row = tk.Frame(self._list_frame, bg=HEADER_BG, cursor="hand2")

        indicator = tk.Label(
            row,
            text=COLLAPSED_INDICATOR,
            bg=HEADER_BG,
            fg="#52525b",
            width=2,
            anchor="center",
        )
        indicator.pack(side=tk.LEFT, padx=(8, 4), pady=8)

        title_label = tk.Label(
            row,
            text=title,
            bg=HEADER_BG,
            fg="#18181b",
            anchor="w",
            justify=tk.LEFT,
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8, padx=(0, 4))

        delete_btn = tk.Label(
            row,
            text="✕",
            bg=HEADER_BG,
            fg="#71717a",
            cursor="hand2",
            padx=8,
            pady=8,
        )
        delete_btn.pack(side=tk.RIGHT)

        if not is_last:
            tk.Frame(row, bg="#d4d4d8", height=1).pack(fill=tk.X, side=tk.BOTTOM)

        row_data = {
            "record": record,
            "row": row,
            "indicator": indicator,
            "title_label": title_label,
            "delete_btn": delete_btn,
        }
        self._rows.append(row_data)

        delete_btn.bind(
            "<Button-1>",
            lambda e, r=record: self._delete_record(r),
        )
        delete_btn.bind(
            "<Enter>",
            lambda e, rd=row_data: self._on_delete_enter(rd),
            add="+",
        )
        delete_btn.bind(
            "<Leave>",
            lambda e, rd=row_data: self._on_delete_leave(rd),
            add="+",
        )

        for widget in (row, indicator, title_label):
            widget.bind(
                "<Button-1>",
                lambda e, r=record: self._toggle_row(r),
                add="+",
            )
            widget.bind(
                "<Enter>",
                lambda e, rd=row_data: self._on_header_enter(rd),
                add="+",
            )
            widget.bind(
                "<Leave>",
                lambda e, rd=row_data: self._on_header_leave(rd),
                add="+",
            )

    def _relayout(self):
        for row_data in self._rows:
            row_data["row"].pack_forget()
        self._detail_frame["frame"].pack_forget()

        for row_data in self._rows:
            row_data["row"].pack(fill=tk.X, side=tk.TOP)
            if row_data["record"]["id"] == self._expanded_record_id:
                self._detail_frame["frame"].pack(
                    fill=tk.X, side=tk.TOP, padx=4, pady=(0, 4)
                )

        self.update_idletasks()
        self._sync_list_frame_height(self._canvas.winfo_height())
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _header_bg(self, row_data):
        if row_data["record"]["id"] == self._expanded_record_id:
            return HEADER_BG_ACTIVE
        return HEADER_BG

    def _on_header_enter(self, row_data):
        if row_data["record"]["id"] != self._expanded_record_id:
            self._set_header_style(row_data, HEADER_BG_HOVER)

    def _on_header_leave(self, row_data):
        self._set_header_style(row_data, self._header_bg(row_data))

    def _set_header_style(self, row_data, bg):
        for key in ("row", "indicator", "title_label", "delete_btn"):
            row_data[key].configure(bg=bg)

    def _on_delete_enter(self, row_data):
        row_data["delete_btn"].configure(fg="#dc2626")

    def _on_delete_leave(self, row_data):
        row_data["delete_btn"].configure(fg="#71717a", bg=self._header_bg(row_data))

    def _delete_record(self, record):
        keys = record.keys() if hasattr(record, "keys") else record
        execution_id = record["execution_id"] if "execution_id" in keys else None
        if execution_id:
            delete_plugin_history_execution(execution_id)
        else:
            delete_plugin_history_entry(record["id"])
        self.refresh()

    def _set_indicator(self, row_data, expanded):
        row_data["indicator"].configure(
            text=EXPANDED_INDICATOR if expanded else COLLAPSED_INDICATOR
        )

    def _toggle_row(self, record):
        if self._expanded_record_id == record["id"]:
            self._collapse_detail()
            return
        self._expand_row(record)

    def _collapse_detail(self):
        for row_data in self._rows:
            self._set_indicator(row_data, False)
            self._set_header_style(row_data, HEADER_BG)
        self._expanded_record_id = None
        self._relayout()

    def _expand_row(self, record):
        for row_data in self._rows:
            expanded = row_data["record"]["id"] == record["id"]
            self._set_indicator(row_data, expanded)
            self._set_header_style(
                row_data, HEADER_BG_ACTIVE if expanded else HEADER_BG
            )

        self._expanded_record_id = record["id"]
        self._set_readonly_text(
            self._detail_frame["input"]["widget"], record["input"] or ""
        )
        self._set_readonly_text(
            self._detail_frame["output"]["widget"], record["output"] or ""
        )
        self._detail_frame["paste_input_btn"].configure(
            command=lambda t=record["input"] or "": paste_text_to_input(
                self._input_text_area, t
            )
        )
        self._detail_frame["paste_output_btn"].configure(
            command=lambda t=record["output"] or "": paste_text_to_input(
                self._input_text_area, t
            )
        )
        self._render_chain_summary(record)
        self._relayout()

    def _reset_chain_summary(self):
        count_label = self._detail_frame["steps_count"]
        count_label.pack_forget()
        count_label._tooltip_text = ""
        self._detail_frame["show_steps_btn"].grid_remove()

    def _render_chain_summary(self, record):
        self._reset_chain_summary()
        if not is_chain_history_row(record):
            return

        step_count = count_execution_steps(record["execution_id"])
        if not step_count:
            return

        count_label = self._detail_frame["steps_count"]
        count_label.configure(text=f"({step_count})")
        count_label._tooltip_text = f"{step_count} steps have been run"
        count_label.pack(side=tk.TOP, before=self._detail_frame["arrow"])

        button = self._detail_frame["show_steps_btn"]
        button.configure(
            command=lambda r=record: self._open_step_details(r)
        )
        button.grid()

    def _open_step_details(self, record):
        rows = fetch_execution_steps(record["execution_id"])
        steps = [
            {
                "label": history_step_label(step),
                "output": step["output"] or "",
            }
            for step in rows
        ]
        HistoryStepDetailsWindow(
            self,
            history_row_title(record),
            record["input"] or "",
            steps,
        )

    @staticmethod
    def _bind_tooltip(widget):
        """Show widget._tooltip_text on hover; nothing when it is empty."""
        widget._tooltip_text = ""
        widget._tooltip_popup = None

        def show(_event=None):
            text = getattr(widget, "_tooltip_text", "")
            if not text or widget._tooltip_popup is not None:
                return
            popup = tk.Toplevel(widget)
            popup.wm_overrideredirect(True)
            popup.wm_geometry(
                f"+{widget.winfo_rootx()}+{widget.winfo_rooty() - 26}"
            )
            tk.Label(
                popup,
                text=text,
                bg="#18181b",
                fg="white",
                padx=6,
                pady=3,
            ).pack()
            widget._tooltip_popup = popup

        def hide(_event=None):
            if widget._tooltip_popup is not None:
                widget._tooltip_popup.destroy()
                widget._tooltip_popup = None

        widget.bind("<Enter>", show, add="+")
        widget.bind("<Leave>", hide, add="+")

    @staticmethod
    def _set_readonly_text(text_widget, content):
        text_widget.configure(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", content)
        text_widget.configure(state=tk.DISABLED)
