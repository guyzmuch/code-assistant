from plugins.plugin import IoMode, Plugin


class CountWords(Plugin):
    DEFAULT_NAME = "Count words"
    IO_MODE = IoMode.MANY_TO_ONE

    def get_description(self):
        return "Count the total number of words in the input lines"

    def run(self, user_input_list):
        """
        hello world
        foo bar baz
        """
        count = sum(len(line.split()) for line in user_input_list)
        return [str(count)]
