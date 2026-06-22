import json

from plugins.plugin import Plugin
from utils.format import format_error, json_dumps, parse_json_lenient
from utils.text import merge_lines_into_one


class StringifyJson(Plugin):
    DEFAULT_NAME = "Stringify JSON"

    def get_description(self):
        return "Parse JSON from input and stringify it"

    def run(self, user_input_list):
        """
        {"b":2,"a":1}
        """
        try:
            input_as_one_line = merge_lines_into_one(user_input_list)
            data = parse_json_lenient(input_as_one_line)
            return [json_dumps(data, pretty=True)]
        except (ValueError, json.JSONDecodeError) as e:
            return [format_error(str(e))]
