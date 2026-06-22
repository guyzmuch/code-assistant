import tkinter as tk
from tkinter import messagebox, ttk

from app.config import load_app_config, save_app_config
from app.context import get
from app.plugins_loader import discover_plugin_classes
from database.plugins_registry import archive_plugin, fetch_configured_plugins
from views.main_layout import apply_text_font_size
from views.settings.plugin_config_dialog import PluginConfigDialog


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.transient(parent)
        self.grab_set()
        self.geometry("750x520")
        self.minsize(600, 400)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._general_tab = ttk.Frame(notebook, padding=10)
        self._plugins_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self._general_tab, text="General")
        notebook.add(self._plugins_tab, text="Plugins")

        self._build_general_tab()
        self._build_plugins_tab()

    def _build_general_tab(self):
        config = load_app_config()

        self._general_tab.columnconfigure(1, weight=1)

        ttk.Label(self._general_tab, text="Text size:").grid(
            row=0, column=0, sticky="w", pady=4
        )
        self._font_size_var = tk.IntVar(value=config["text_font_size"])
        font_spinbox = ttk.Spinbox(
            self._general_tab,
            from_=8,
            to=24,
            textvariable=self._font_size_var,
            width=6,
        )
        font_spinbox.grid(row=0, column=1, sticky="w", pady=4)

        self._history_startup_var = tk.BooleanVar(
            value=config["history_open_at_startup"]
        )
        ttk.Checkbutton(
            self._general_tab,
            text="Open history panel at startup",
            variable=self._history_startup_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=4)

        ttk.Button(
            self._general_tab,
            text="Save",
            command=self._save_general,
        ).grid(row=2, column=0, columnspan=2, sticky="e", pady=(16, 0))

    def _save_general(self):
        config = {
            "text_font_size": self._font_size_var.get(),
            "history_open_at_startup": self._history_startup_var.get(),
        }
        save_app_config(config)
        apply_text_font_size(get().layout, config["text_font_size"])

    def _build_plugins_tab(self):
        self._plugins_tab.rowconfigure(0, weight=1)
        self._plugins_tab.columnconfigure(0, weight=1)

        paned = ttk.Panedwindow(self._plugins_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        configured_frame = ttk.LabelFrame(paned, text="Configured plugins", padding=8)
        available_frame = ttk.LabelFrame(paned, text="Available plugins", padding=8)
        paned.add(configured_frame, weight=1)
        paned.add(available_frame, weight=1)

        configured_frame.rowconfigure(0, weight=1)
        configured_frame.columnconfigure(0, weight=1)
        available_frame.rowconfigure(0, weight=1)
        available_frame.columnconfigure(0, weight=1)

        configured_list_frame = ttk.Frame(configured_frame)
        configured_list_frame.grid(row=0, column=0, sticky="nsew")
        configured_list_frame.rowconfigure(0, weight=1)
        configured_list_frame.columnconfigure(0, weight=1)

        self._configured_listbox = tk.Listbox(configured_list_frame, exportselection=False)
        configured_scroll = ttk.Scrollbar(
            configured_list_frame,
            orient=tk.VERTICAL,
            command=self._configured_listbox.yview,
        )
        self._configured_listbox.configure(yscrollcommand=configured_scroll.set)
        self._configured_listbox.grid(row=0, column=0, sticky="nsew")
        configured_scroll.grid(row=0, column=1, sticky="ns")

        configured_buttons = ttk.Frame(configured_frame)
        configured_buttons.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(configured_buttons, text="Edit", command=self._edit_plugin).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(
            configured_buttons, text="Remove", command=self._remove_plugin
        ).pack(side=tk.LEFT)

        available_canvas = tk.Canvas(available_frame, highlightthickness=0)
        available_scroll = ttk.Scrollbar(
            available_frame,
            orient=tk.VERTICAL,
            command=available_canvas.yview,
        )
        self._available_inner = ttk.Frame(available_canvas)
        self._available_inner.bind(
            "<Configure>",
            lambda e: available_canvas.configure(
                scrollregion=available_canvas.bbox("all")
            ),
        )
        self._available_window = available_canvas.create_window(
            (0, 0), window=self._available_inner, anchor="nw"
        )
        available_canvas.configure(yscrollcommand=available_scroll.set)
        available_canvas.grid(row=0, column=0, sticky="nsew")
        available_scroll.grid(row=0, column=1, sticky="ns")

        def _on_canvas_configure(event):
            available_canvas.itemconfig(self._available_window, width=event.width)

        available_canvas.bind("<Configure>", _on_canvas_configure)

        self._configured_rows = []
        self._plugin_classes_by_name = {
            plugin_class.__name__: plugin_class
            for plugin_class in discover_plugin_classes()
        }

        self._refresh_configured_list()
        self._populate_available_plugins()

    def _display_name_for_row(self, row):
        if row["custom_name"]:
            return row["custom_name"]
        plugin_class = self._plugin_classes_by_name.get(row["name"])
        if plugin_class:
            return plugin_class.DEFAULT_NAME
        return row["name"]

    def _refresh_configured_list(self):
        self._configured_listbox.delete(0, tk.END)
        self._configured_rows = list(fetch_configured_plugins())
        for row in self._configured_rows:
            self._configured_listbox.insert(tk.END, self._display_name_for_row(row))

    def _populate_available_plugins(self):
        for child in self._available_inner.winfo_children():
            child.destroy()

        for plugin_class in sorted(
            discover_plugin_classes(), key=lambda cls: cls.DEFAULT_NAME.lower()
        ):
            row = ttk.Frame(self._available_inner)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=plugin_class.DEFAULT_NAME).pack(
                side=tk.LEFT, fill=tk.X, expand=True
            )
            ttk.Button(
                row,
                text="Add",
                command=lambda cls=plugin_class: self._add_plugin(cls),
            ).pack(side=tk.RIGHT)

    def _selected_configured_row(self):
        selection = self._configured_listbox.curselection()
        if not selection:
            return None
        return self._configured_rows[selection[0]]

    def _on_plugins_changed(self):
        self._refresh_configured_list()
        get().repopulate_plugins()

    def _add_plugin(self, plugin_class):
        PluginConfigDialog(
            self,
            plugin_class=plugin_class,
            on_saved=self._on_plugins_changed,
        )

    def _edit_plugin(self):
        row = self._selected_configured_row()
        if row is None:
            messagebox.showwarning(
                "Edit plugin", "Select a configured plugin first.", parent=self
            )
            return

        plugin_class = self._plugin_classes_by_name.get(row["name"])
        if plugin_class is None:
            messagebox.showerror(
                "Edit plugin",
                f"Plugin class {row['name']} is not available.",
                parent=self,
            )
            return

        PluginConfigDialog(
            self,
            plugin_class=plugin_class,
            plugin_row=row,
            on_saved=self._on_plugins_changed,
        )

    def _remove_plugin(self):
        row = self._selected_configured_row()
        if row is None:
            messagebox.showwarning(
                "Remove plugin", "Select a configured plugin first.", parent=self
            )
            return

        label = self._display_name_for_row(row)
        if not messagebox.askyesno(
            "Remove plugin",
            f"Remove configured plugin \"{label}\"?",
            parent=self,
        ):
            return

        archive_plugin(row["id"])
        self._on_plugins_changed()


def open_settings_window(parent):
    SettingsWindow(parent)
