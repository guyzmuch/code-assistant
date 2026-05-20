import hashlib
import hmac

from plugins.plugin import Plugin
from utils.format import format_error
from utils.text import apply_for_all_lines


def validate_algorithm(algorithm: str, key: str = "") -> None:
    try:
        if key:
            hmac.new(b"", b"", algorithm)
        else:
            hashlib.new(algorithm, b"")
    except (ValueError, TypeError) as e:
        raise ValueError(f"unsupported algorithm: {algorithm}") from e


def hash_line(
    line: str,
    algorithm: str,
    prefix: str = "",
    suffix: str = "",
    key: str = "",
) -> str:
    message = f"{prefix}{line}{suffix}".encode("utf-8")

    if key:
        return hmac.new(key.encode("utf-8"), message, algorithm).hexdigest()

    return hashlib.new(algorithm, message).hexdigest()


class HashLines(Plugin):
    DEFAULT_NAME = "Hash lines"
    DEFAULT_OPTIONS = {
        "algorithm": "sha256",
        "prefix": "",
        "suffix": "",
        "key": "",
    }

    def get_description(self):
        return (
            "Hash each input line (hex digest). Set options as JSON, e.g. "
            '{"algorithm": "sha256", "prefix": "", "suffix": "", "key": ""}. '
            "algorithm: digest name from hashlib (sha256, sha512, md5, blake2b, sha3_256, ...). "
            "prefix: static text prepended to each line. "
            "suffix: static text appended to each line. "
            "key: when set, uses HMAC with this key instead of a plain hash."
        )

    def run(self, user_input_list):
        """
        hello
        world
        """
        algorithm = self.options["algorithm"]
        prefix = self.options["prefix"]
        suffix = self.options["suffix"]
        key = self.options["key"]

        try:
            validate_algorithm(algorithm, key)
        except ValueError as e:
            return [format_error(str(e))]

        def hash_one_line(line: str) -> str:
            return hash_line(line, algorithm, prefix, suffix, key)

        return apply_for_all_lines(user_input_list, hash_one_line)
