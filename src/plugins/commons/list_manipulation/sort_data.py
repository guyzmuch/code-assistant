from plugins.plugin import IoMode, Plugin
from utils.text import remove_empty_lines


class SortData(Plugin):
    DEFAULT_NAME = "Sort data"
    IO_MODE = IoMode.SAME_COUNT
    DEFAULT_OPTIONS = {
        "reverse": False,
        "trim": True,
        "remove_empty_lines": True,
    }

    def get_description(self):
        return "Sort input lines in ascending or descending order"

    def run(self, user_input_list):
        """
        cherry
        apple
        banana
        """
        lines = list(user_input_list)

        if self.options["remove_empty_lines"]:
            lines = remove_empty_lines(lines)

        if self.options["trim"]:
            trimmed = []
            for line in lines:
                trimmed.append(line.strip())
            lines = trimmed

        return sorted(lines, reverse=self.options["reverse"])
