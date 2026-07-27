from app.context import get, refresh_history_if_visible
from app.plugins_loader import discover_plugin_classes
from app.recent_plugins import record_plugin_run
from database.plugin_history import HistoryRecorder
from database.plugins_registry import fetch_chain_steps
from plugins.plugin_chain import PluginChain
from plugins.runnable import Runnable
from utils.ui import split_lines


def _plugins_by_class_name():
    return {
        plugin_class.__name__: plugin_class
        for plugin_class in discover_plugin_classes()
    }


def _instantiate_plugin(row, plugins_by_name):
    plugin_class = plugins_by_name.get(row["name"])
    if plugin_class is None:
        return None
    return plugin_class(
        custom_name=row["custom_name"],
        options=row["options"],
        shortcut=row["shortcut"],
        id=row["id"],
        config_version=row["config_version"],
    )


def load_runnable(row, plugins_by_name=None) -> Runnable | None:
    """Turn a configured top-level row into a runnable.

    A standalone row becomes a Plugin; a chain header (chain_position 0) loads
    its ordered steps and becomes a PluginChain. Both implement Runnable.
    """
    if plugins_by_name is None:
        plugins_by_name = _plugins_by_class_name()

    if row["chain_id"] is None:
        return _instantiate_plugin(row, plugins_by_name)

    steps = []
    for step_row in fetch_chain_steps(row["chain_id"]):
        plugin = _instantiate_plugin(step_row, plugins_by_name)
        if plugin is not None:
            steps.append(plugin)
    return PluginChain(
        custom_name=row["custom_name"],
        steps=steps,
        id=row["id"],
        config_version=row["config_version"],
        shortcut=row["shortcut"],
    )


def plugin_entrance(runnable: Runnable):
    ctx = get()
    input_text_area = ctx.layout.user_input_text_area

    user_input_list = split_lines(input_text_area)
    output_list = runnable.execute(user_input_list, HistoryRecorder())
    output_text = "\n".join(output_list)
    ctx.layout.set_output_text(output_text)

    record_plugin_run(runnable)
    refresh_history_if_visible()
    from app.menu import repopulate_plugins_menu

    repopulate_plugins_menu()
