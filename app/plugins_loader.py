import importlib
import os

from database.plugins_registry import register_plugin_classes

PLUGINS_DIR = "plugins"
EXCLUDED_FILES = {"__init__.py", "plugin.py"}


def discover_plugin_classes():
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
    plugin_classes = discover_plugin_classes()
    register_plugin_classes(db_connection, plugin_classes)
    return plugin_classes
