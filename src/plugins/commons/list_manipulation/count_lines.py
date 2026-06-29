from plugins.plugin import Plugin


class CountLines(Plugin):
    DEFAULT_NAME = "Count lines"

    def get_description(self):
        return "Count the number of input lines"

    def run(self, user_input_list):
        """
        apple
        banana

        cherry
        """
        return [str(len(user_input_list))]
