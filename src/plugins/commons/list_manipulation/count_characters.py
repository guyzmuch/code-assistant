from plugins.plugin import Plugin


def _should_count(char, exclude_spaces, exclude_symbols):
    if exclude_spaces and char.isspace():
        return False
    if exclude_symbols:
        return char.isalnum() or char.isspace()
    return True


class CountCharacters(Plugin):
    DEFAULT_NAME = "Count characters"
    DEFAULT_OPTIONS = {"exclude_spaces": False, "exclude_symbols": False}

    def get_description(self):
        return "Count the total number of characters in the input lines"

    def run(self, user_input_list):
        """
        hello, world!
        foo bar
        """
        exclude_spaces = self.options["exclude_spaces"]
        exclude_symbols = self.options["exclude_symbols"]
        count = sum(
            1
            for line in user_input_list
            for char in line
            if _should_count(char, exclude_spaces, exclude_symbols)
        )
        return [str(count)]
