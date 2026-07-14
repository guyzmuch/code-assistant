from plugins.commons.string_manipulation.change_case import ChangeCase


class TestChangeCase:
    def test_capitalize_first_letter(self):
        plugin = ChangeCase(options='{"case": "capitalize_first"}')
        result = plugin.run(["hello", "WORLD", "hELLO wORLD"])

        assert result == ["Hello", "WORLD", "HELLO wORLD"]

    def test_uppercase(self):
        plugin = ChangeCase(options='{"case": "uppercase"}')
        result = plugin.run(["hello", "World", "MiXeD"])

        assert result == ["HELLO", "WORLD", "MIXED"]

    def test_lowercase(self):
        plugin = ChangeCase(options='{"case": "lowercase"}')
        result = plugin.run(["HELLO", "World", "MiXeD"])

        assert result == ["hello", "world", "mixed"]

    def test_default_is_capitalize_first(self):
        plugin = ChangeCase()
        result = plugin.run(["hello world"])

        assert result == ["Hello world"]

    def test_preserves_empty_lines(self):
        plugin = ChangeCase(options='{"case": "uppercase"}')
        result = plugin.run(["hello", "", "world"])

        assert result == ["HELLO", "", "WORLD"]
