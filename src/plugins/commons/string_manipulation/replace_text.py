import ast
import re

from plugins.plugin import IoMode, Plugin
from utils.format import format_error
from utils.text import apply_for_all_lines


def parse_search_pattern(search: str) -> tuple[bool, str]:
    """
    Return (is_regex, pattern).

    Plain text is matched literally. A Python raw string literal (r"..." or r'...')
    is compiled as a regex, the same syntax used in Python source code.
    """
    if len(search) >= 3 and search[0] in "rR" and search[1] in "\"'":
        try:
            pattern = ast.literal_eval(search)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"invalid regex literal: {e}") from e
        if not isinstance(pattern, str):
            raise ValueError("regex literal must evaluate to a string")
        return True, pattern
    return False, search


def replace_in_line(
    line: str,
    *,
    is_regex: bool,
    pattern: str,
    replacement: str,
    case_sensitive: bool = False,
) -> str:
    flags = 0 if case_sensitive else re.IGNORECASE
    if is_regex:
        return re.sub(pattern, replacement, line, flags=flags)
    if case_sensitive:
        return line.replace(pattern, replacement)
    return re.sub(re.escape(pattern), replacement, line, flags=flags)


class ReplaceText(Plugin):
    DEFAULT_NAME = "Replace text"
    IO_MODE = IoMode.SAME_COUNT
    DEFAULT_OPTIONS_SCHEMA = {
        "search": {
            "type": "string",
            "label": "Search",
            "description": (
                "Text to find on each line. Plain text is matched literally "
                '(e.g. hello). For a regex, use a Python raw string literal: '
                'r"\\d+" or r\'foo|bar\' (prefix r before the quotes, as in Python).'
            ),
            "default": "",
        },
        "replace": {
            "type": "string",
            "label": "Replace with",
            "description": (
                "Replacement text. With regex search, backreferences are supported "
                '(e.g. search r"(\\d+)" and replace "num: \\1").'
            ),
            "default": "",
        },
        "case_sensitive": {
            "type": "boolean",
            "label": "Case sensitive",
            "description": (
                "When enabled, search matches letter case exactly. "
                "When disabled (default), matching ignores case."
            ),
            "default": False,
        },
    }

    def get_description(self):
        return "Replace text on each input line using a literal search or a regex"

    def run(self, user_input_list):
        """
        hello world
        foo bar foo
        order 42
        """
        search = self.options["search"]
        replacement = self.options["replace"]
        case_sensitive = self.options["case_sensitive"]

        if not search:
            return [format_error("no search text provided")]

        try:
            is_regex, pattern = parse_search_pattern(search)
        except ValueError as e:
            return [format_error(str(e))]

        flags = 0 if case_sensitive else re.IGNORECASE
        if is_regex:
            try:
                re.compile(pattern, flags=flags)
            except re.error as e:
                return [format_error(str(e))]

        def replace_line(line: str) -> str:
            return replace_in_line(
                line,
                is_regex=is_regex,
                pattern=pattern,
                replacement=replacement,
                case_sensitive=case_sensitive,
            )

        return apply_for_all_lines(user_input_list, replace_line)
