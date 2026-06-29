import re

from plugins.plugin import Plugin
from utils.format import format_error
from utils.text import apply_for_all_lines


def _flatten_matches(output_list):
    flattened = []
    for item in output_list:
        if item == "":
            flattened.append("")
        elif isinstance(item, list):
            if item:
                flattened.extend(item)
            else:
                flattened.append("")
        else:
            flattened.append(item)
    return flattened


class ExtractByRegex(Plugin):
    DEFAULT_NAME = "Extract by regex"
    DEFAULT_OPTIONS = {"regex": ""}

    def get_description(self):
        return "Extract all regex matches from each input line"

    def run(self, user_input_list):
        """
        contact: alice@example.com, bob@example.org
        no email here
        carol@test.io
        """
        regex = self.options["regex"]
        if not regex:
            return [format_error("no regex provided")]

        try:
            pattern = re.compile(regex)
        except re.error as e:
            return [format_error(str(e))]

        def extract_line(line):
            return [match.group(0) for match in pattern.finditer(line)]

        return _flatten_matches(apply_for_all_lines(user_input_list, extract_line))
