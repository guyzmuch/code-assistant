from plugins.plugin import Plugin
from utils.text import remove_empty_lines


class RemoveDuplicates(Plugin):
    DEFAULT_NAME = "Remove duplicates"
    DEFAULT_OPTIONS = {
        "trim": True,
        "remove_empty_lines": True,
    }

    def get_description(self):
        return "Remove duplicate lines while keeping the first occurrence of each"

    def run(self, user_input_list):
        """
        apple
        banana
        apple
        cherry
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

        return list(dict.fromkeys(lines))
