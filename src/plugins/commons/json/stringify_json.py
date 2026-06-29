import json

from plugins.plugin import Plugin
from utils.format import format_error, json_dumps, parse_json_lenient
from utils.text import merge_lines_into_one


def _extract_json_text(text: str) -> str:
    """Keep only the JSON object or array from noisy input.

    Finds the first ``{`` or ``[`` and slices through the last matching ``}``
    or ``]``. Assumes a single JSON value in the text (e.g. embedded in HTML
    or a function call). Returns the input unchanged when no opener is found.
    """
    start = next((index for index, char in enumerate(text) if char in "{["), None)
    if start is None:
        return text

    closer = "}" if text[start] == "{" else "]"
    end = text.rfind(closer)
    if end < start:
        return text[start:]
    return text[start : end + 1]


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
            extracted_json = _extract_json_text(input_as_one_line)
            data = parse_json_lenient(extracted_json)
            return [json_dumps(data, pretty=True)]
        except (ValueError, json.JSONDecodeError) as e:
            return [format_error(str(e))]
