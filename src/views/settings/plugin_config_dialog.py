import json
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk

from database.plugins_registry import create_plugin, update_plugin
from views.settings.options_form import OptionsForm


class PluginConfigDialog(tk.Toplevel):
    def __init__(
        self,
        parent,
        *,
        plugin_class,
        plugin_row=None,
        on_saved,
    ):
        super().__init__(parent)
        self._plugin_class = plugin_class
        self._plugin_row = plugin_row
        self._on_saved = on_saved
        self._is_edit = plugin_row is not None

        title = "Edit plugin" if self._is_edit else "Add plugin"
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        self.configure(bg="white")

        body = ttk.Frame(self, padding=10)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(3, weight=1)

        ttk.Label(body, text="Plugin:").grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            body,
            text=plugin_class.DEFAULT_NAME,
        ).grid(row=0, column=1, sticky="w", pady=(0, 4))

        ttk.Label(body, text="Custom name:").grid(
            row=1, column=0, sticky="w", pady=4
        )
        self._name_var = tk.StringVar()
        name_entry = ttk.Entry(body, textvariable=self._name_var)
        name_entry.grid(row=1, column=1, sticky="ew", pady=4)

        schema = getattr(plugin_class, "DEFAULT_OPTIONS_SCHEMA", None)
        self._uses_form = bool(schema)

        if self._uses_form:
            existing_values = self._parse_options(
                plugin_row["options"] if self._is_edit else None
            )
            self._options_form = OptionsForm(
                body, schema, values=existing_values
            )
            self._options_form.grid(
                row=3, column=0, columnspan=2, sticky="nsew", pady=4
            )
        else:
            ttk.Label(body, text="Options (JSON):").grid(
                row=2, column=0, sticky="nw", pady=4
            )
            self._options_text = scrolledtext.ScrolledText(
                body,
                height=12,
                width=50,
                bg="white",
                fg="black",
                insertbackground="black",
            )
            self._options_text.grid(
                row=3, column=0, columnspan=2, sticky="nsew", pady=4
            )

        buttons = ttk.Frame(body)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
        ttk.Button(buttons, text="Save", command=self._save).pack(side=tk.RIGHT)

        if self._is_edit:
            self._name_var.set(plugin_row["custom_name"] or "")
            if not self._uses_form:
                self._options_text.insert("1.0", plugin_row["options"] or "{}")
        else:
            self._name_var.set(plugin_class.DEFAULT_NAME)
            if not self._uses_form:
                self._options_text.insert("1.0", "{}")

        self.geometry("500x400")
        name_entry.focus_set()

    @staticmethod
    def _parse_options(options):
        if not options:
            return {}
        try:
            parsed = json.loads(options)
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _save(self):
        custom_name = self._name_var.get()
        if self._uses_form:
            options = json.dumps(self._options_form.get_values())
        else:
            options = self._options_text.get("1.0", "end-1c")

        if self._is_edit:
            update_plugin(
                self._plugin_row["id"],
                custom_name,
                options,
            )
        else:
            create_plugin(
                self._plugin_class.__name__,
                custom_name,
                options,
            )

        self._on_saved()
        self.destroy()
