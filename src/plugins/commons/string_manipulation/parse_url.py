from urllib.parse import parse_qs, urlparse

from plugins.plugin import IoMode, Plugin
from utils.format import format_error, json_dumps
from utils.text import merge_lines_into_one


def _query_to_object(query_string: str) -> dict:
    parsed = parse_qs(query_string, keep_blank_values=True)
    query = {}
    for key, values in parsed.items():
        if len(values) == 1:
            query[key] = values[0]
        else:
            query[key] = values
    return query


class ParseUrl(Plugin):
    DEFAULT_NAME = "Parse URL to JSON"
    IO_MODE = IoMode.ONE_TO_ONE
    DEFAULT_OPTIONS = {"query_only": False, "pretty": True}

    def get_description(self):
        return "Parse a URL into JSON using urllib.parse"

    def run(self, user_input_list):
        """
        https://www.w3schools.com/html/default.asp?para1=value1&para2=value2#section1
        """
        try:
            url = merge_lines_into_one(user_input_list).replace("\n", "")
            parsed = urlparse(url)

            if self.options["query_only"]:
                data = _query_to_object(parsed.query)
            else:
                data = {
                    "fragment": parsed.fragment,
                    "hostname": parsed.hostname,
                    "href": url,
                    "netloc": parsed.netloc,
                    "password": parsed.password,
                    "path": parsed.path,
                    "path_parts": [
                        part for part in parsed.path.split("/") if part
                    ],
                    "port": parsed.port,
                    "query": _query_to_object(parsed.query),
                    "scheme": parsed.scheme,
                    "username": parsed.username,
                }

            return [json_dumps(data, pretty=self.options["pretty"])]
        except ValueError as e:
            return [format_error(str(e))]
