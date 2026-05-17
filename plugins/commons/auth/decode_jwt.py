import base64
import json

from plugins.plugin import Plugin
from utils.format import format_error, format_section


def _decode_jwt_part(segment: str) -> dict:
    padding = "=" * (-len(segment) % 4)
    decoded = base64.urlsafe_b64decode(segment + padding)
    return json.loads(decoded)


def _json_dumps(data: dict, pretty: bool) -> str:
    if pretty:
        return json.dumps(data, indent=2, sort_keys=True)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


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

    payload_json = _json_dumps(payload, pretty)
    if payload_only:
        return payload_json

    header_json = _json_dumps(header, pretty)
    return "\n".join(
        [
            format_section("HEADER"),
            header_json,
            format_section("PAYLOAD"),
            payload_json,
        ]
    )


class DecodeJwt(Plugin):
    DEFAULT_NAME = "Decode JWT"
    DEFAULT_OPTIONS = {"payload_only": False, "pretty": True}

    def get_description(self):
        return "Decode JWT header and payload from the first input line"

    def run(self, user_input_list):
        """
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature
        """
        if not user_input_list:
            return [format_error("no input provided")]

        token = user_input_list[0]
        if not token.strip():
            return [format_error("first line is empty")]

        try:
            return [_format_jwt(token, self.options)]
        except Exception as e:
            return [format_error(str(e))]
