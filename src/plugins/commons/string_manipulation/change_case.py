from plugins.plugin import IoMode, Plugin
from utils.text import apply_for_all_lines

_CASE_TRANSFORMERS = {
    "capitalize_first": lambda line: line[0].upper() + line[1:] if line else line,
    "uppercase": str.upper,
    "lowercase": str.lower,
}


class ChangeCase(Plugin):
    DEFAULT_NAME = "Change case"
    IO_MODE = IoMode.SAME_COUNT
    DEFAULT_OPTIONS_SCHEMA = {
        "case": {
            "type": "select",
            "label": "Case",
            "description": "How to transform each input line",
            "choices": ["capitalize_first", "uppercase", "lowercase"],
        },
    }

    def get_description(self):
        return (
            "Transforms each input line: capitalize the first letter only, "
            "convert to uppercase, or convert to lowercase."
        )

    def run(self, user_input_list):
        """
        hello
        WORLD
        """
        case = self.options["case"]
        transform = _CASE_TRANSFORMERS[case]
        return apply_for_all_lines(user_input_list, transform)
