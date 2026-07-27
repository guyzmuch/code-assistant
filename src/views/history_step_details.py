import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

_TEXT_WIDTH = 17
_TEXT_HEIGHT = 16
_DETAIL_BG = "#fafafa"
_SEPARATOR_FG = "#a1a1aa"
_TITLE_WRAP = 150


class HistoryStepDetailsWindow(tk.Toplevel):
    """Shows a chain execution's steps laid out left-to-right.

    Because each step's output is the next step's input, those shared values are
    merged into a single column: the row reads original input, then each step's
    plugin and its result, ending on the final output. The columns scroll
    horizontally and each text box is capped in size.

    Titles sit in one grid row (bottom-aligned) so every text area starts on
    the same line — under the tallest title — even when some headings wrap.
    """

    def __init__(self, parent, chain_title, input_text, steps):
        super().__init__(parent)
        self.title(f"Chain steps — {chain_title}")
        self.transient(parent)
        self.geometry("900x460")
        self.minsize(480, 320)

        header = ttk.Frame(self, padding=(10, 8))
        header.pack(fill=tk.X)
        ttk.Label(
            header,
            text=f"{len(steps)} steps have been run",
            font=tkfont.Font(size=11, weight="bold"),
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(self, highlightthickness=0, bg=_DETAIL_BG)
        hscroll = ttk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=canvas.xview
        )
        inner = ttk.Frame(canvas)
        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(xscrollcommand=hscroll.set)
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)

        self._build_columns(inner, input_text, steps)

    def _build_columns(self, inner, input_text, steps):
        columns = [("Original input", input_text)]
        last_index = len(steps) - 1
        for index, step in enumerate(steps):
            base = (
                "Final output"
                if index == last_index
                else f"After step {index + 1}"
            )
            columns.append((f"{base} ({step['label']})", step["output"]))

        # Row 0 = titles (sticky south so short titles sit at the bottom of
        # the tallest one). Row 1 = text areas, all starting on the same line.
        grid_col = 0
        for index, (heading, text) in enumerate(columns):
            if index > 0:
                # Only alongside the text areas — not the title row — so there
                # is no white strip between the step names.
                tk.Label(
                    inner,
                    text="›",
                    fg=_SEPARATOR_FG,
                    bg=_DETAIL_BG,
                    font=tkfont.Font(size=14),
                ).grid(row=1, column=grid_col, sticky="ns", padx=2)
                grid_col += 1

            ttk.Label(
                inner,
                text=heading,
                anchor="sw",
                justify=tk.LEFT,
                wraplength=_TITLE_WRAP,
            ).grid(row=0, column=grid_col, sticky="sw", padx=4, pady=(0, 4))

            text_frame = ttk.Frame(inner)
            text_frame.grid(row=1, column=grid_col, sticky="nw", padx=4)
            self._fill_text(text_frame, text)
            grid_col += 1

    def _fill_text(self, text_frame, text):
        widget = tk.Text(
            text_frame,
            width=_TEXT_WIDTH,
            height=_TEXT_HEIGHT,
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d4d4d8",
            highlightcolor="#d4d4d8",
            bg="white",
            fg="#18181b",
            padx=8,
            pady=8,
        )
        vscroll = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=widget.yview
        )
        widget.configure(yscrollcommand=vscroll.set)
        widget.insert("1.0", text or "")
        widget.configure(state=tk.DISABLED)
        widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
