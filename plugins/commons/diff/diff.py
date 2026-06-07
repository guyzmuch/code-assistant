import difflib

import pyperclip

from plugins.plugin import Plugin
from utils.format import format_error
from utils.text import require_input


class Diff(Plugin):
    DEFAULT_NAME = "Diff"

    def get_description(self):
        return "Diff input against the clipboard (unified diff)"

    def run(self, user_input_list):
        try:
            require_input(user_input_list)
            clipboard_lines = pyperclip.paste().splitlines()
            return list(
                difflib.unified_diff(
                    user_input_list,
                    clipboard_lines,
                    fromfile="input",
                    tofile="clipboard",
                    lineterm="",
                )
            )
        except ValueError as e:
            return [format_error(str(e))]
