import importlib
import os

from app.constants import DEFAULT_PLUGIN_CLASS_NAMES
from database.plugins_registry import count_active_plugins, create_plugin

PLUGINS_DIR = "plugins"
EXCLUDED_FILES = {"__init__.py", "plugin.py"}


def discover_plugin_classes():
    """Return the list of the plugin files present in the project"""
    plugin_classes = []

    for root, _dirs, files in os.walk(PLUGINS_DIR):
        for file in files:
            if not file.endswith(".py") or file in EXCLUDED_FILES:
                continue

            rel_path = os.path.relpath(os.path.join(root, file), ".")
            module_path = rel_path.replace(os.sep, ".")[:-3]

            module = importlib.import_module(module_path)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "__bases__")
                    and any(base.__name__ == "Plugin" for base in attr.__bases__)
                ):
                    plugin_classes.append(attr)

    return plugin_classes


def load_plugins(db_connection):
    return discover_plugin_classes()


def plugin_category(plugin_class):
    parts = plugin_class.__module__.split(".")
    if len(parts) >= 2:
        return parts[-2]
    return "other"


def ensure_default_plugins(db_connection):
    """Seed the database on first run when no configured plugins exist yet."""
    if count_active_plugins(db_connection) > 0:
        return

    plugin_classes = discover_plugin_classes()

    # Only auto-configure plugins listed in DEFAULT_PLUGIN_CLASS_NAMES;
    # other discovered plugins stay available to add manually in Settings.
    default_classes = [
        plugin_class
        for plugin_class in plugin_classes
        if plugin_class.__name__ in DEFAULT_PLUGIN_CLASS_NAMES
    ]

    for plugin_class in default_classes:
        create_plugin(db_connection, plugin_class.__name__)
