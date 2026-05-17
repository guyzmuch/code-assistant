from plugins.plugin import Plugin


class JoinByComma(Plugin):
    DEFAULT_NAME = "Join by comma"

    def get_description(self):
        return "Strip each line and join non-empty lines with a comma"

    def get_options(self):
        return {}

    def run(self, user_input_list):
        """
        apple
        banana
        cherry
        """
        items = [line.strip() for line in user_input_list if line.strip()]
        return [",".join(items)]
