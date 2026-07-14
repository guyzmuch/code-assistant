# DevToolbelt — Agent Guide

Desktop Tkinter app for transforming text/data via plugins. Product name: **DevToolbelt**. Repo folder: `code-assistant`.

## App introduction
The DevToolbelt app is in short word a configurable OS app.  
The idea is that you have an input, you select a plugin to execute, the plugin will process the input and display it in the output.  

The interface is mainly that: an input text area, a list of plugin, an output text area.

The user can configure the plugins by passing it options, but the "root" plugins are a set of files in the application.  
Plugins could be formating the input (joining by character, uppercase), of transforming it (convert to timestamp to date, hashing) or any other process.  
The configured plugins are save in a sqlite database.  
Each plugin execution is saved in a sqlite database for history retrival and re-run


## Quick commands

Activate the virtual environment first — without it, run and test commands will fail (missing dependencies / wrong Python):

```bash
source venv/bin/activate
```

One-time setup if `venv/` does not exist yet:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# for tests/build: pip install -r requirements-dev.txt
```

```bash
# Run (dev) — ./run.sh activates venv for you
./run.sh
# or, with venv already active:
PYTHONPATH=src python src/main.py

# Tests (venv must be active)
PYTHONPATH=src pytest src/tests
PYTHONPATH=src pytest src/tests -v

# Build executable (venv must be active)
./scripts/build.sh
```

Python 3.12+. `PYTHONPATH=src` is required for tests and direct runs.

## Layout

```
src/
  main.py              # entry point
  app/                 # application logic (menu, config, plugin loading, window)
  views/               # Tkinter UI (layout, dialogs, history panel, settings)
  plugins/             # plugin classes (discovered automatically)
  database/            # SQLite (plugins registry, history)
  utils/               # shared helpers
  tests/               # pytest (mirrors src structure)
assets/                # icons
docs/                  # user-facing docs (minimal today)
```

## Architecture

- **Plugins** are Python classes subclassing `Plugin` in `src/plugins/plugin.py`. They are discovered by walking the `plugins` package (`app/plugins_loader.py`).
- **Configured plugins** live in SQLite (`database/plugins_registry.py`). The same plugin class can appear multiple times with different names/options.
- **App context** (`app/context.py`) holds the DB connection, layout, and history panel. Prefer `app.context.db_connection()` over threading `db_connection` through call chains.
- **UI** is Tkinter with `grid` layout. Settings use JSON-schema-style option forms (`views/settings/options_form.py`).

## Database schema
### plugins table
User can see the list of plugins and configure some to be seen on the interface. After the configuration, the plugin and its configuration is saved in this table.  

Columns: 
- id: identifier
- name: name of the plugin file that is the base of the plugin
- custom_name: Name that is displayed on the app, set by the user
- options: a JSON object with key/value for the different option configured by the user
- shortcut: keyboard shortcut to activate the plugin
- config_version: get incremented on each update of the plugin
- archived: soft delete of configured plugin
- show_in_panel: is the plugin should be displayed on the panel, or on the menu


### plugin_history table
Keep history of all the plugin execution for easy retrieval

Columns:
- id: identifier
- input: text inserted as input for the execution
- output: text outputed at the execution
- plugin_id: id of the plugin from the "plugin" table
- config_version: version of the plugin the execution run on 
- timestamp: time of the execution


## Adding a plugin

1. Create a module under `src/plugins/<category>/` (e.g. `plugins/commons/string_manipulation/`).
2. Subclass `Plugin` and set `DEFAULT_NAME`.
3. Implement `get_description()` and `run(self, user_input_list) -> list[str]`.
4. Define options via `DEFAULT_OPTIONS_SCHEMA` (preferred) or `DEFAULT_OPTIONS`.
5. Add tests under `src/tests/plugins/...`.

`run` receives a list of input lines and returns a list of output lines (often one element).

### Plugin options schema
`DEFAULT_OPTIONS_SCHEMA` should have a format of :
- key: key name of the options, that will be used to be saved in the database
- type: string, number, boolean or select
- label: user front name for the option
- description: what that option doer
- default: default value of the options if none is set
- choices: in case of a select the list of options (the first entry is the default)

Example: 
```
{
  "foo": {
    "type": "string",
    "label": "Foo",
    "description": "This is foo",
    "default": "foo"
  },
  "bar": {
    "type": "number",
    "label": "Number of bar",
    "description": "Number of bar",
    "default": 42
  },
  // example of a select options
  "speed": {
    "type": "select",
    "label": "Speed",
    "description": "the speed",
    "choices": ["fast", "slow"]
  }
}
```

A plugin can have multiple options. On the interface, when the user is configuring the plugin, he gets a form with the different values. those values are already set with their default.  
When saving the plugin configuration, the plugin is saved in the plugin.db under the "plugin" table column "options" and save as a key/value, example:
```
{
  "foo": "my custom string",
  "bar": 42,
  "speed: "fast"
}
```


## Utils helpers

Shared helpers for plugins. Reuse these instead of reimplementing the same logic.

### `src/utils/format.py`

- **`format_section(title)`** — Returns a section header string: `--- {title}`.
- **`format_error(message)`** — Returns a multi-line error block with divider lines and a `---- ERROR ----` label. Use for user-visible plugin errors.
- **`json_dumps(data, pretty)`** — Serializes `data` to JSON. When `pretty` is true, uses 2-space indent; otherwise compact output. Keys are always sorted.
- **`parse_json_lenient(text)`** — Parses JSON with fallbacks: strict `json.loads` first, then unicode-escape decoding, then unwraps a top-level JSON string value if present. Raises `json.JSONDecodeError` if all attempts fail.

### `src/utils/text.py`

- **`require_input(lines)`** — Raises `ValueError("no input provided")` if `lines` is empty. Use at the start of plugins that need input.
- **`first_non_empty_line(lines)`** — Returns the first line with non-whitespace content. Raises if `lines` is empty or all lines are blank.
- **`merge_lines_into_one(lines)`** — Joins all lines with `\n`, strips the result, and raises if the combined text is empty. For plugins that treat multi-line input as one value.
- **`apply_for_all_lines(lines, function)`** — Applies `function` to each non-empty line; empty lines are passed through unchanged. Per-line exceptions become `"Error: {e}"` strings in the output instead of failing the whole run.
- **`remove_empty_lines(lines)`** — Returns a new list with whitespace-only lines removed.
- **`flatten_and_remove_empty_lines(output_list)`** — Flattens a list of lists (or iterables) into one list and drops falsy items (empty strings).

## Conventions

- Match existing plugin and test style; keep changes focused.
- Do not commit secrets or local data (`config.json`, `plugins.db`, `venv/`, `temp.txt`).
- Version string: `src/app/version.py`.
- Process name on Linux: `app/branding.py` (`set_process_name`).
- Only create git commits when explicitly asked.


