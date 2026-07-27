from plugins.plugin import IoMode, Plugin
from utils.text import apply_for_all_lines, flatten_and_remove_empty_lines

QUOTE_CHARS = "\"'`‘’“”"
QUOTE_TABLE = str.maketrans("", "", QUOTE_CHARS)

def _strip_quotes(value):
    # Using translate to replace all quote characters with an empty string
    return value.translate(QUOTE_TABLE)

class SplitBySeparator(Plugin):
    DEFAULT_NAME = "Split by separator"
    IO_MODE = IoMode.ONE_TO_MANY
    DEFAULT_OPTIONS = {"separator": ",", "trim": True, "strip_quotes": False}

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
        strip_quotes = self.options["strip_quotes"]

        def split_line(line):
            parts = line.split(separator)
            if trim:
                parts = [part.strip() for part in parts]
            if strip_quotes:
                parts = [_strip_quotes(part) for part in parts]
            return parts

        output_list = apply_for_all_lines(user_input_list, split_line)
        return flatten_and_remove_empty_lines(output_list)
