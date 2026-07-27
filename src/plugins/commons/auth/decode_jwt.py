import base64
import datetime
import json

from plugins.plugin import IoMode, Plugin
from utils.format import format_error, format_section, json_dumps
from utils.text import first_non_empty_line

_MIN_UNIX_SECONDS = 1_000_000_000
_MAX_UNIX_SECONDS = 4_000_000_000
_MAX_UNIX_MILLISECONDS = 4_000_000_000_000


def _decode_jwt_part(segment: str) -> dict:
    padding = "=" * (-len(segment) % 4)
    decoded = base64.urlsafe_b64decode(segment + padding)
    return json.loads(decoded)


def _collect_timestamps(data, prefix=""):
    if not isinstance(data, dict):
        return None

    timestamps = []
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            number = int(value)
            if _MIN_UNIX_SECONDS <= number <= _MAX_UNIX_SECONDS:
                timestamps.append((path, datetime.datetime.fromtimestamp(number)))
            elif _MIN_UNIX_SECONDS * 1000 <= number <= _MAX_UNIX_MILLISECONDS:
                timestamps.append((path, datetime.datetime.fromtimestamp(number / 1000)))
        elif isinstance(value, dict):
            nested = _collect_timestamps(value, path)
            if nested:
                timestamps.extend(nested)

    return timestamps or None


def _format_extra_data(payload: dict) -> str | None:
    timestamps = _collect_timestamps(payload)
    if timestamps is None:
        return None

    lines = []
    for path, dt in timestamps:
        lines.append(f"{path}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(lines)


def _format_jwt(token: str, options: dict) -> str:
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("Invalid JWT: expected header and payload segments")

    header = _decode_jwt_part(parts[0])
    payload = _decode_jwt_part(parts[1])
    pretty = options["pretty"]
    payload_only = options["payload_only"]

    payload_json = json_dumps(payload, pretty)

    if payload_only:
        return payload_json

    header_json = json_dumps(header, pretty)
    sections = [
        format_section("HEADER"),
        header_json,
        format_section("PAYLOAD"),
        payload_json,
    ]

    extra_data = _format_extra_data(payload)
    if extra_data:
        sections.append(format_section("EXTRA DATA"))
        sections.append(extra_data)
    return "\n".join(sections)


class DecodeJwt(Plugin):
    DEFAULT_NAME = "Decode JWT"
    IO_MODE = IoMode.ONE_TO_ONE
    DEFAULT_OPTIONS = {"payload_only": False, "pretty": True}

    def get_description(self):
        return "Decode JWT header and payload from the first input line"

    def run(self, user_input_list):
        """
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature
        """
        try:
            token = first_non_empty_line(user_input_list)
            return [_format_jwt(token, self.options)]
        except ValueError as e:
            return [format_error(str(e))]
