from plugins.plugin import Plugin
from utils.text import apply_for_all_lines, flatten_and_remove_empty_lines


class SplitBySeparator(Plugin):
    DEFAULT_NAME = "Split by separator"
    DEFAULT_OPTIONS = {"separator": ",", "trim": True}

    def get_description(self):
        return "Split each line by a configurable separator and flatten the result"

    def run(self, user_input_list):
        """
        apple , banana , cherry
        orange  ,  grape  ,  kiwi
        citron,mango,pear,pineapple,
        """
        separator = self.options["separator"]
        trim = self.options["trim"]

        def split_line(line):
            parts = line.split(separator)
            if trim:
                parts = [part.strip() for part in parts]
            return parts

        output_list = apply_for_all_lines(user_input_list, split_line)
        return flatten_and_remove_empty_lines(output_list)
