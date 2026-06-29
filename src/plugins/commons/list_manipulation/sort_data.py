from plugins.plugin import Plugin


class SortData(Plugin):
    DEFAULT_NAME = "Sort data"
    DEFAULT_OPTIONS = {"reverse": False}

    def get_description(self):
        return "Sort input lines in ascending or descending order"

    def run(self, user_input_list):
        """
        cherry
        apple
        banana
        """
        return sorted(user_input_list, reverse=self.options["reverse"])
