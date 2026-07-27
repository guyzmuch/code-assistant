import re

from plugins.plugin import IoMode, Plugin
from utils.format import format_error
from utils.text import apply_for_all_lines


class ValidateByRegex(Plugin):
    DEFAULT_NAME = "Validate by regex"
    IO_MODE = IoMode.SAME_COUNT
    DEFAULT_OPTIONS = {"regex": ""}

    def get_description(self):
        return "Check each input line against a regex and output valid or invalid"

    def run(self, user_input_list):
        """
        alice@example.com
        not-an-email
        bob@example.org
        """
        regex = self.options["regex"]
        if not regex:
            return [format_error("no regex provided")]

        try:
            pattern = re.compile(regex)
        except re.error as e:
            return [format_error(str(e))]

        def validate_line(line):
            return "valid" if pattern.search(line) else "invalid"

        return apply_for_all_lines(user_input_list, validate_line)
