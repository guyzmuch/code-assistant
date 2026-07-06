from plugins.plugin import Plugin


class JoinBySeparator(Plugin):
    DEFAULT_NAME = "Join by separator"
    DEFAULT_OPTIONS = {
        "separator": ",",
        "trim": True,
        "skip_empty_lines": True,
        "item_wrap": "",
    }

    def get_description(self):
        return "Join lines using a configurable separator"

    def run(self, user_input_list):
        """
        apple
        banana
        cherry
        """
        separator = self.options["separator"]
        trim = self.options["trim"]
        skip_empty_lines = self.options["skip_empty_lines"]
        item_wrap = self.options["item_wrap"]

        items = []
        for line in user_input_list:
            value = line.strip() if trim else line
            if skip_empty_lines and not value:
                continue
            items.append(f"{item_wrap}{value}{item_wrap}")

        return [separator.join(items)]
