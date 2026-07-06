from app.recent_plugins import (
    RecentPluginEntry,
    clear_recent_plugins,
    get_recent_plugins,
    record_plugin_run,
)
from plugins.plugin import Plugin


class _AlphaPlugin(Plugin):
    DEFAULT_NAME = "Alpha"

    def get_description(self):
        return "alpha"

    def run(self, user_input_list):
        return user_input_list


class _BetaPlugin(Plugin):
    DEFAULT_NAME = "Beta"

    def get_description(self):
        return "beta"

    def run(self, user_input_list):
        return user_input_list


def _plugin_class(class_name, default_name):
    def get_description(self):
        return default_name

    def run(self, user_input_list):
        return user_input_list

    return type(
        class_name,
        (Plugin,),
        {
            "DEFAULT_NAME": default_name,
            "get_description": get_description,
            "run": run,
        },
    )


def setup_function():
    clear_recent_plugins()


def test_record_plugin_run_moves_duplicate_to_front():
    record_plugin_run(_AlphaPlugin())
    record_plugin_run(_BetaPlugin())
    record_plugin_run(_AlphaPlugin())

    recent = get_recent_plugins()

    assert len(recent) == 2
    assert recent[0] == RecentPluginEntry(plugin_name="_AlphaPlugin")
    assert recent[1] == RecentPluginEntry(plugin_name="_BetaPlugin")


def test_record_plugin_run_keeps_configured_plugins_separate_by_id():
    configured_a = _AlphaPlugin(id=1, config_version=1)
    configured_b = _AlphaPlugin(id=2, config_version=1)

    record_plugin_run(configured_a)
    record_plugin_run(configured_b)

    recent = get_recent_plugins()

    assert len(recent) == 2
    assert recent[0].plugin_id == 2
    assert recent[1].plugin_id == 1


def test_record_plugin_run_limits_to_ten_entries():
    for index in range(12):
        plugin_class = _plugin_class(f"_Plugin{index}", f"Plugin {index}")
        record_plugin_run(plugin_class())

    recent = get_recent_plugins()

    assert len(recent) == 10
    assert recent[0].plugin_name == "_Plugin11"
    assert recent[-1].plugin_name == "_Plugin2"
