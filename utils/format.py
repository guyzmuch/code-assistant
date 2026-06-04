import json

_ERROR_DIVIDER = "--------------------"


def format_section(title: str) -> str:
    return f"--- {title}"


def format_error(message: str) -> str:
    return (
        f"{_ERROR_DIVIDER}\n"
        f"---- ERROR ----\n"
        f"\n"
        f"{message}\n"
        f"{_ERROR_DIVIDER}"
    )


def json_dumps(data, pretty: bool) -> str:
    if pretty:
        return json.dumps(data, indent=2, sort_keys=True)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def parse_json_lenient(text: str):
    """Parse JSON, trying strict parse, then escaped text, then a JSON string wrapper."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as first_error:
        try:
            data = json.loads(text.encode("utf-8").decode("unicode_escape"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise first_error from None

    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass
    return data
