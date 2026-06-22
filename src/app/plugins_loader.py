import importlib
import pkgutil

import plugins

from app.constants import DEFAULT_PLUGIN_CLASS_NAMES
from database.plugins_registry import count_active_plugins, create_plugin


def discover_plugin_classes():
    """Return plugin classes by importing every module under the plugins package."""
    plugin_classes = []
    prefix = plugins.__name__ + "."

    for module_info in pkgutil.walk_packages(plugins.__path__, prefix):
        if module_info.name.endswith(".plugin"):
            continue

        module = importlib.import_module(module_info.name)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and hasattr(attr, "__bases__")
                and any(base.__name__ == "Plugin" for base in attr.__bases__)
            ):
                plugin_classes.append(attr)

    return plugin_classes


def load_plugins():
    return discover_plugin_classes()


def plugin_category(plugin_class):
    parts = plugin_class.__module__.split(".")
    if len(parts) >= 2:
        return parts[-2]
    return "other"


def ensure_default_plugins():
    """Seed the database on first run when no configured plugins exist yet."""
    if count_active_plugins() > 0:
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
        create_plugin(plugin_class.__name__)
