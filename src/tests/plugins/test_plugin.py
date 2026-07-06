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

    def test_python_literal_options_override_defaults(self):
        plugin = _ExamplePlugin(options='{"separator": ";", "trim": True}')
        assert plugin.options == {"separator": ";", "trim": True}

    def test_invalid_json_falls_back_to_defaults(self):
        plugin = _ExamplePlugin(options="not json")
        assert plugin.options == {"separator": ","}


class _SchemaPlugin(Plugin):
    DEFAULT_NAME = "Schema Plugin"
    DEFAULT_OPTIONS = {"ignored": "should not be used"}
    DEFAULT_OPTIONS_SCHEMA = {
        "separator": {"type": "string", "default": ","},
        "trim": {"type": "boolean", "default": True},
        "text": {"type": "string"},
        "count": {"type": "number"},
        "enabled": {"type": "boolean"},
        "mode": {"type": "select", "choices": ["fast", "slow"]},
        "empty_select": {"type": "select"},
    }

    def get_description(self):
        return "Schema plugin used only in tests"

    def run(self, user_input_list):
        return user_input_list


class TestSchemaOptions:
    def test_schema_defaults_take_precedence_over_default_options(self):
        plugin = _SchemaPlugin()
        assert "ignored" not in plugin.options

    def test_explicit_schema_defaults_are_used(self):
        plugin = _SchemaPlugin()
        assert plugin.options["separator"] == ","
        assert plugin.options["trim"] is True

    def test_per_type_fallback_defaults(self):
        plugin = _SchemaPlugin()
        assert plugin.options["text"] == ""
        assert plugin.options["count"] == 0
        assert plugin.options["enabled"] is False

    def test_select_fallback_uses_first_choice(self):
        plugin = _SchemaPlugin()
        assert plugin.options["mode"] == "fast"

    def test_select_without_choices_falls_back_to_empty_string(self):
        plugin = _SchemaPlugin()
        assert plugin.options["empty_select"] == ""

    def test_passed_options_override_schema_defaults(self):
        plugin = _SchemaPlugin(options='{"separator": ";", "count": 5}')
        assert plugin.options["separator"] == ";"
        assert plugin.options["count"] == 5
        assert plugin.options["trim"] is True
