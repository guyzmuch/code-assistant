import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk

from database.plugins_registry import create_plugin, update_plugin


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

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text="Plugin:").grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 4)
        )
        ttk.Label(
            self,
            text=plugin_class.DEFAULT_NAME,
        ).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(10, 4))

        ttk.Label(self, text="Custom name:").grid(
            row=1, column=0, sticky="w", padx=10, pady=4
        )
        self._name_var = tk.StringVar()
        name_entry = ttk.Entry(self, textvariable=self._name_var)
        name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=4)

        ttk.Label(self, text="Options (JSON):").grid(
            row=2, column=0, sticky="nw", padx=10, pady=4
        )
        self._options_text = scrolledtext.ScrolledText(self, height=12, width=50)
        self._options_text.grid(
            row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=4
        )

        buttons = ttk.Frame(self)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", padx=10, pady=10)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
        ttk.Button(buttons, text="Save", command=self._save).pack(side=tk.RIGHT)

        if self._is_edit:
            self._name_var.set(plugin_row["custom_name"] or "")
            self._options_text.insert("1.0", plugin_row["options"] or "{}")
        else:
            self._name_var.set(plugin_class.DEFAULT_NAME)
            self._options_text.insert("1.0", "{}")

        self.geometry("500x400")
        name_entry.focus_set()

    def _save(self):
        custom_name = self._name_var.get()
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
