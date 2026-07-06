from dataclasses import dataclass

MAX_RECENT_PLUGINS = 10

_recent_plugins: list["RecentPluginEntry"] = []


@dataclass(frozen=True)
class RecentPluginEntry:
    plugin_name: str
    plugin_id: int | None = None


def _entry_key(entry: RecentPluginEntry):
    if entry.plugin_id is not None:
        return ("id", entry.plugin_id)
    return ("class", entry.plugin_name)


def record_plugin_run(plugin) -> None:
    entry = RecentPluginEntry(
        plugin_name=type(plugin).__name__,
        plugin_id=plugin.id,
    )
    key = _entry_key(entry)
    global _recent_plugins
    _recent_plugins = [e for e in _recent_plugins if _entry_key(e) != key]
    _recent_plugins.insert(0, entry)
    del _recent_plugins[MAX_RECENT_PLUGINS:]


def get_recent_plugins() -> list[RecentPluginEntry]:
    return list(_recent_plugins)


def clear_recent_plugins() -> None:
    _recent_plugins.clear()
