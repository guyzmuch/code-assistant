import json
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import messagebox, ttk

from app.context import plugin_classes, plugins_by_name
from database.plugins_registry import (
    create_chain,
    fetch_chain_steps,
    update_chain,
)
from views.settings.options_form import OptionsForm


class ChainConfigDialog(tk.Toplevel):
    """Create or edit a chain: a name plus an ordered list of plugin steps."""

    def __init__(self, parent, *, chain_row=None, on_saved):
        super().__init__(parent)
        self._chain_row = chain_row
        self._on_saved = on_saved
        self._is_edit = chain_row is not None

        self._classes_by_name = plugins_by_name()
        self._classes_by_label = {
            cls.DEFAULT_NAME: cls
            for cls in sorted(
                plugin_classes(),
                key=lambda cls: cls.DEFAULT_NAME.lower(),
            )
        }
        # steps: list of {"cls": plugin_class, "options": dict}
        self._steps = []

        self.title("Edit chain" if self._is_edit else "Add chain")
        self.transient(parent)
        self.grab_set()
        self.geometry("560x520")
        self.minsize(480, 400)

        body = ttk.Frame(self, padding=10)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(3, weight=1)

        ttk.Label(body, text="Chain name:").grid(
            row=0, column=0, sticky="w", pady=4
        )
        self._name_var = tk.StringVar()
        name_entry = ttk.Entry(body, textvariable=self._name_var)
        name_entry.grid(row=0, column=1, sticky="ew", pady=4)

        self._show_in_panel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            body,
            text="Show in plugin panel",
            variable=self._show_in_panel_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=4)

        ttk.Label(body, text="Steps (run top to bottom):").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 4)
        )

        steps_container = ttk.Frame(body)
        steps_container.grid(row=3, column=0, columnspan=2, sticky="nsew")
        steps_container.rowconfigure(0, weight=1)
        steps_container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(steps_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            steps_container, orient=tk.VERTICAL, command=canvas.yview
        )
        self._steps_frame = ttk.Frame(canvas)
        self._steps_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        steps_window = canvas.create_window(
            (0, 0), window=self._steps_frame, anchor="nw"
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(steps_window, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        ttk.Button(body, text="Add step", command=self._add_step).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        buttons = ttk.Frame(body)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
        ttk.Button(buttons, text="Save", command=self._save).pack(
            side=tk.RIGHT
        )

        self._load_initial_state()
        name_entry.focus_set()

    def _load_initial_state(self):
        if self._is_edit:
            self._name_var.set(self._chain_row["custom_name"] or "")
            self._show_in_panel_var.set(
                bool(self._chain_row["show_in_panel"])
            )
            for step_row in fetch_chain_steps(self._chain_row["chain_id"]):
                cls = self._classes_by_name.get(step_row["name"])
                if cls is None:
                    continue
                self._steps.append(
                    {
                        "cls": cls,
                        "options": _parse_options(step_row["options"]),
                    }
                )
        self._render_steps()

    def _default_class(self):
        labels = list(self._classes_by_label.keys())
        return self._classes_by_label[labels[0]] if labels else None

    def _add_step(self):
        cls = self._default_class()
        if cls is None:
            messagebox.showerror(
                "Add step", "No plugins are available.", parent=self
            )
            return
        self._steps.append({"cls": cls, "options": {}})
        self._render_steps()

    def _render_steps(self):
        for child in self._steps_frame.winfo_children():
            child.destroy()

        if not self._steps:
            ttk.Label(
                self._steps_frame,
                text="No steps yet. Click \"Add step\" to build the pipeline.",
                foreground="#71717a",
            ).grid(row=0, column=0, sticky="w", pady=6, padx=4)
            return

        self._steps_frame.columnconfigure(1, weight=1)
        for index, step in enumerate(self._steps):
            ttk.Label(self._steps_frame, text=f"{index + 1}.").grid(
                row=index, column=0, sticky="w", padx=(4, 4), pady=3
            )

            label_var = tk.StringVar(value=step["cls"].DEFAULT_NAME)
            combo = ttk.Combobox(
                self._steps_frame,
                textvariable=label_var,
                values=list(self._classes_by_label.keys()),
                state="readonly",
            )
            combo.grid(row=index, column=1, sticky="ew", pady=3)
            combo.bind(
                "<<ComboboxSelected>>",
                lambda e, i=index, v=label_var: self._on_step_class_changed(
                    i, v.get()
                ),
            )

            actions = ttk.Frame(self._steps_frame)
            actions.grid(row=index, column=2, sticky="e", padx=(4, 4))
            ttk.Button(
                actions,
                text="Options…",
                width=8,
                command=lambda i=index: self._configure_step(i),
            ).pack(side=tk.LEFT, padx=(0, 2))
            ttk.Button(
                actions,
                text="↑",
                width=2,
                command=lambda i=index: self._move_step(i, -1),
            ).pack(side=tk.LEFT)
            ttk.Button(
                actions,
                text="↓",
                width=2,
                command=lambda i=index: self._move_step(i, 1),
            ).pack(side=tk.LEFT)
            ttk.Button(
                actions,
                text="✕",
                width=2,
                command=lambda i=index: self._remove_step(i),
            ).pack(side=tk.LEFT, padx=(2, 0))

    def _on_step_class_changed(self, index, label):
        cls = self._classes_by_label.get(label)
        if cls is None or cls is self._steps[index]["cls"]:
            return
        # Options are plugin-specific, so reset them when the plugin changes.
        self._steps[index] = {"cls": cls, "options": {}}
        self._render_steps()

    def _configure_step(self, index):
        step = self._steps[index]
        _StepOptionsDialog(
            self,
            plugin_class=step["cls"],
            values=step["options"],
            on_saved=lambda options: self._set_step_options(index, options),
        )

    def _set_step_options(self, index, options):
        self._steps[index]["options"] = options

    def _move_step(self, index, delta):
        target = index + delta
        if target < 0 or target >= len(self._steps):
            return
        self._steps[index], self._steps[target] = (
            self._steps[target],
            self._steps[index],
        )
        self._render_steps()

    def _remove_step(self, index):
        del self._steps[index]
        self._render_steps()

    def _save(self):
        custom_name = self._name_var.get().strip()
        if not custom_name:
            messagebox.showwarning(
                "Save chain", "Give the chain a name.", parent=self
            )
            return
        if not self._steps:
            messagebox.showwarning(
                "Save chain", "Add at least one step.", parent=self
            )
            return

        steps_payload = [
            {
                "name": step["cls"].__name__,
                "options": json.dumps(step["options"]),
            }
            for step in self._steps
        ]
        show_in_panel = self._show_in_panel_var.get()

        if self._is_edit:
            update_chain(
                self._chain_row["chain_id"],
                custom_name,
                steps_payload,
                show_in_panel=show_in_panel,
            )
        else:
            create_chain(
                custom_name,
                steps_payload,
                show_in_panel=show_in_panel,
            )

        self._on_saved()
        self.destroy()


class _StepOptionsDialog(tk.Toplevel):
    """Edit one chain step's options, reusing the plugin OptionsForm."""

    def __init__(self, parent, *, plugin_class, values, on_saved):
        super().__init__(parent)
        self._plugin_class = plugin_class
        self._on_saved = on_saved

        self.title(f"Options — {plugin_class.DEFAULT_NAME}")
        self.transient(parent)
        self.grab_set()
        self.geometry("460x360")

        body = ttk.Frame(self, padding=10)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        schema = getattr(plugin_class, "DEFAULT_OPTIONS_SCHEMA", None)
        self._uses_form = bool(schema)

        if self._uses_form:
            self._options_form = OptionsForm(body, schema, values=values)
            self._options_form.grid(row=0, column=0, sticky="nsew")
        else:
            self._options_text = scrolledtext.ScrolledText(
                body, height=12, bg="white", fg="black", insertbackground="black"
            )
            self._options_text.grid(row=0, column=0, sticky="nsew")
            self._options_text.insert(
                "1.0", json.dumps(values or {}, indent=2)
            )

        buttons = ttk.Frame(body)
        buttons.grid(row=1, column=0, sticky="e", pady=(10, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
        ttk.Button(buttons, text="Save", command=self._save).pack(
            side=tk.RIGHT
        )

    def _save(self):
        if self._uses_form:
            options = self._options_form.get_values()
        else:
            options = _parse_options(self._options_text.get("1.0", "end-1c"))
        self._on_saved(options)
        self.destroy()


def _parse_options(options):
    if not options:
        return {}
    try:
        parsed = json.loads(options)
    except (json.JSONDecodeError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}
