import tkinter as tk
from tkinter import ttk

_TYPE_FALLBACKS = {
    "string": "",
    "number": 0,
    "boolean": False,
}

_LABEL_MIN_WIDTH = 140


def _field_default(field):
    if "default" in field:
        return field["default"]

    field_type = field.get("type", "string")
    if field_type == "select":
        choices = field.get("choices") or []
        return choices[0] if choices else ""
    return _TYPE_FALLBACKS.get(field_type, "")


class OptionsForm(ttk.Frame):
    """Builds a form from a plugin options schema and reads typed values back."""

    def __init__(self, parent, schema, values=None):
        super().__init__(parent)
        # Column 0 (labels) is fixed so every input in column 1 lines up,
        # regardless of how long a given label is.
        self.columnconfigure(0, weight=0, minsize=_LABEL_MIN_WIDTH)
        self.columnconfigure(1, weight=1)

        self._schema = schema
        values = values or {}
        self._vars = {}
        self._types = {}
        self._help_popup = None

        for row, (name, field) in enumerate(schema.items()):
            field_type = field.get("type", "string")
            label = field.get("label", name)
            description = field.get("description")

            initial = values[name] if name in values else _field_default(field)
            self._types[name] = field_type

            ttk.Label(self, text=label, wraplength=_LABEL_MIN_WIDTH).grid(
                row=row, column=0, sticky="w", padx=(0, 8), pady=4
            )

            if field_type == "boolean":
                var = tk.BooleanVar(value=bool(initial))
                widget = ttk.Checkbutton(self, variable=var)
            else:
                var = tk.StringVar(value="" if initial is None else str(initial))
                if field_type == "select":
                    widget = ttk.Combobox(
                        self,
                        textvariable=var,
                        values=list(field.get("choices") or []),
                        state="readonly",
                    )
                elif field_type == "number":
                    widget = ttk.Spinbox(
                        self, textvariable=var, from_=0, to=1_000_000
                    )
                else:
                    widget = ttk.Entry(self, textvariable=var)

            widget.grid(row=row, column=1, sticky="ew", pady=4)
            self._vars[name] = var

            if description:
                self._build_help_icon(row, description)

    def _build_help_icon(self, row, description):
        size = 15
        icon = tk.Canvas(
            self,
            width=size,
            height=size,
            highlightthickness=0,
            bg=self.winfo_toplevel().cget("bg"),
            cursor="hand2",
        )
        oval = icon.create_oval(
            1, 1, size - 1, size - 1, fill="#b0b7c0", outline=""
        )
        icon.create_text(
            size / 2 + 1,
            size / 2,
            text="?",
            fill="white",
            font=("TkDefaultFont", 9, "bold"),
        )
        icon.grid(row=row, column=2, sticky="w", padx=(6, 0))

        icon.bind("<Enter>", lambda e: icon.itemconfigure(oval, fill="#6b7280"))
        icon.bind("<Leave>", lambda e: icon.itemconfigure(oval, fill="#b0b7c0"))
        icon.bind(
            "<Button-1>",
            lambda e, a=icon, d=description: self._toggle_help(a, d),
        )

    def _toggle_help(self, anchor, text):
        if self._help_popup is not None:
            self._help_popup.destroy()
            self._help_popup = None
            return

        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.wm_geometry(
            f"+{anchor.winfo_rootx()}"
            f"+{anchor.winfo_rooty() + anchor.winfo_height() + 2}"
        )
        tk.Label(
            popup,
            text=text,
            background="#ffffe0",
            foreground="black",
            relief="solid",
            borderwidth=1,
            justify="left",
            wraplength=250,
            padx=6,
            pady=4,
        ).pack()

        def _close(_event=None):
            if self._help_popup is not None:
                self._help_popup.destroy()
                self._help_popup = None

        popup.bind("<Leave>", _close)
        popup.bind("<Button-1>", _close)
        self._help_popup = popup

    def get_values(self):
        result = {}
        for name, var in self._vars.items():
            field_type = self._types[name]
            if field_type == "boolean":
                result[name] = bool(var.get())
            elif field_type == "number":
                result[name] = self._coerce_number(name, var.get())
            else:
                result[name] = var.get()
        return result

    def _coerce_number(self, name, text):
        text = (text or "").strip()
        try:
            return float(text) if "." in text else int(text)
        except ValueError:
            return _field_default(self._schema[name])
