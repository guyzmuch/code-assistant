from unittest.mock import patch

from plugins.commons.diff.diff import Diff, build_diff_segments, _line_tag


class TestBuildDiffSegments:
    def test_skips_unified_diff_headers(self):
        segments = build_diff_segments(["plop", "foo"], ["plop", "bar"])

        texts = [text.rstrip("\n") for text, _ in segments]
        assert "--- input" not in texts
        assert "+++ clipboard" not in texts
        assert not any(text.startswith("@@") for text in texts)

    def test_tags_added_removed_and_context(self):
        segments = build_diff_segments(["plop", "foo"], ["plop", "bar"])

        assert segments == [
            (" plop\n", "diff_context"),
            ("-foo\n", "diff_removed"),
            ("+bar\n", "diff_added"),
        ]

    def test_identical_texts_produce_no_segments(self):
        assert build_diff_segments(["a", "b"], ["a", "b"]) == []


class TestLineTag:
    def test_maps_diff_prefixes(self):
        assert _line_tag("+x") == "diff_added"
        assert _line_tag("-x") == "diff_removed"
        assert _line_tag(" x") == "diff_context"


class TestDiff:
    def test_run_returns_content_lines_without_headers(self):
        plugin = Diff()
        with patch("pyperclip.paste", return_value="plop\nbar"):
            result = plugin.run(["plop", "foo"])

        assert "--- input" not in result
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
