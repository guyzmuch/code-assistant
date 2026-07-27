import re

from plugins.plugin import IoMode, Plugin
from utils.text import apply_for_all_lines

_VALUE_PLACEHOLDER = re.compile(r"\{value_(\d+)\}")


def substitute_values(template: str, values: list[str]) -> str:
    """Replace {value_1}, {value_2}, ... with values[0], values[1], ... (1-based)."""

    def replacer(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if 1 <= index <= len(values):
            return values[index - 1]
        return ""

    return _VALUE_PLACEHOLDER.sub(replacer, template)


class ApplyTemplate(Plugin):
    DEFAULT_NAME = "Apply template"
    IO_MODE = IoMode.ANY_TO_ANY
    DEFAULT_OPTIONS = {
        "template": ["{value_1}"],
    }

    def get_description(self):
        return (
            "Outputs one line per template string. Configure options as JSON with a "
            '"template" array, e.g. {"template": ["Hello {value_1}", "ID: {value_2}"]}. '
            "Use {value_1}, {value_2}, ... as placeholders; input line 1 replaces "
            "{value_1}, line 2 replaces {value_2}. Missing lines become empty."
        )

    def run(self, user_input_list):
        """
        hello
        """
        templates = self.options["template"]

        def apply_template(template: str) -> str:
            return substitute_values(template, user_input_list)

        return apply_for_all_lines(templates, apply_template)
