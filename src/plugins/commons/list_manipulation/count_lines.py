from plugins.plugin import IoMode, Plugin


class CountLines(Plugin):
    DEFAULT_NAME = "Count lines"
    IO_MODE = IoMode.MANY_TO_ONE

    def get_description(self):
        return "Count the number of input lines"

    def run(self, user_input_list):
        """
        apple
        banana

        cherry
        """
        return [str(len(user_input_list))]
