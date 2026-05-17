import pytest

from plugins.plugin import Plugin


class _ExamplePlugin(Plugin):
    DEFAULT_NAME = "Example Plugin"
    DEFAULT_OPTIONS = {"separator": ","}

    def get_description(self):
        return "Example plugin used only in tests"

    def run(self, user_input_list):
        return user_input_list


class TestDefaultName:
    def test_missing_default_name_raises_at_class_definition(self):
        with pytest.raises(TypeError, match="must define DEFAULT_NAME"):

            class _InvalidPlugin(Plugin):
                def get_description(self):
                    return ""

                def run(self, user_input_list):
                    return []


class TestName:
    def test_uses_default_name(self):
        plugin = _ExamplePlugin()
        assert plugin.name == "Example Plugin"
        assert plugin.get_name() == "Example Plugin"

    def test_custom_name_overrides_default_name(self):
        plugin = _ExamplePlugin(custom_name="Custom Label")
        assert plugin.name == "Custom Label"
        assert plugin.custom_name == "Custom Label"

    def test_empty_custom_name_uses_default_name(self):
        plugin = _ExamplePlugin(custom_name="")
        assert plugin.name == "Example Plugin"


class TestOptions:
    def test_uses_default_options_when_none_passed(self):
        plugin = _ExamplePlugin()
        assert plugin.options == {"separator": ","}

    def test_passed_options_override_defaults(self):
        plugin = _ExamplePlugin(options='{"separator": ";"}')
        assert plugin.options == {"separator": ";"}

    def test_passed_options_add_keys(self):
        plugin = _ExamplePlugin(options='{"trim": true}')
        assert plugin.options == {"separator": ",", "trim": True}

    def test_invalid_json_falls_back_to_defaults(self):
        plugin = _ExamplePlugin(options="not json")
        assert plugin.options == {"separator": ","}
