from plugins.commons.string_manipulation.apply_template import (
    ApplyTemplate,
    substitute_values,
)


class TestSubstituteValues:
    def test_replaces_single_placeholder(self):
        result = substitute_values("hello {value_1}", ["world"])
        assert result == "hello world"

    def test_replaces_multiple_placeholders(self):
        result = substitute_values(
            "{value_1} and {value_2}",
            ["alpha", "beta"],
        )
        assert result == "alpha and beta"

    def test_replaces_same_placeholder_multiple_times(self):
        result = substitute_values("item {value_1} plop {value_1}", ["x"])
        assert result == "item x plop x"

    def test_supports_high_index_without_predefining_placeholders(self):
        template = "entry {value_1000}"
        values = [""] * 999 + ["last"]
        result = substitute_values(template, values)
        assert result == "entry last"

    def test_replaces_missing_entry_with_empty_string(self):
        result = substitute_values("missing {value_5}", ["a", "b"])
        assert result == "missing "


class TestApplyTemplate:
    def test_applies_default_template(self):
        plugin = ApplyTemplate()
        result = plugin.run(["hello"])

        assert result == ["hello"]

    def test_uses_custom_templates_from_options(self):
        plugin = ApplyTemplate(
            options='{"template": ["{value_1}-{value_2}", "only {value_3}"]}'
        )
        result = plugin.run(["one", "two", "three"])

        assert result == ["one-two", "only three"]

    def test_handles_more_input_values_than_placeholders(self):
        plugin = ApplyTemplate(options='{"template": ["{value_1}"]}')
        result = plugin.run(["first", "second", "third"])

        assert result == ["first"]

    def test_empty_input_replaces_placeholders_with_empty_strings(self):
        plugin = ApplyTemplate(options='{"template": ["{value_1} and {value_2}"]}')
        result = plugin.run([])

        assert result == [" and "]
