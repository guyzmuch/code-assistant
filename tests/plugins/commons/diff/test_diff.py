from unittest.mock import patch

from plugins.commons.diff.diff import Diff


class TestDiff:
    def test_unified_diff_input_vs_clipboard(self):
        plugin = Diff()
        with patch("pyperclip.paste", return_value="plop\nbar"):
            result = plugin.run(["plop", "foo"])

        assert result[0] == "--- input"
        assert result[1] == "+++ clipboard"
        assert "-foo" in result
        assert "+bar" in result

    def test_identical_input_and_clipboard(self):
        plugin = Diff()
        with patch("pyperclip.paste", return_value="a\nb"):
            result = plugin.run(["a", "b"])

        assert result == []

    def test_empty_input_returns_error(self):
        plugin = Diff()
        result = plugin.run([])[0]

        assert "--- ERROR" in result
        assert "no input provided" in result
