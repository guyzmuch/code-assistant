from plugins.plugin import Plugin


class RemoveDuplicates(Plugin):
    DEFAULT_NAME = "Remove duplicates"

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
        return list(dict.fromkeys(user_input_list))
