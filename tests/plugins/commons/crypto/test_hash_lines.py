import hashlib
import hmac

import pytest

from plugins.commons.crypto.hash_lines import HashLines, hash_line, validate_algorithm
from utils.format import format_error


class TestHashLine:
    def test_sha256_without_prefix_suffix_or_key(self):
        expected = hashlib.sha256(b"hello").hexdigest()
        assert hash_line("hello", "sha256") == expected

    def test_prepends_prefix(self):
        expected = hashlib.sha256(b"pepperhello").hexdigest()
        assert hash_line("hello", "sha256", prefix="pepper") == expected

    def test_appends_suffix(self):
        expected = hashlib.sha256(b"hello!").hexdigest()
        assert hash_line("hello", "sha256", suffix="!") == expected

    def test_uses_prefix_and_suffix(self):
        expected = hashlib.sha256(b"pepperhello!").hexdigest()
        assert hash_line("hello", "sha256", prefix="pepper", suffix="!") == expected

    def test_uses_hmac_when_key_set(self):
        expected = hmac.new(b"key", b"hello", "sha256").hexdigest()
        assert hash_line("hello", "sha256", key="key") == expected

    def test_hmac_includes_prefix_and_suffix_in_message(self):
        expected = hmac.new(b"key", b"pepperhello!", "sha256").hexdigest()
        assert hash_line("hello", "sha256", prefix="pepper", suffix="!", key="key") == expected

    def test_supports_other_algorithms(self):
        expected = hashlib.sha512(b"test").hexdigest()
        assert hash_line("test", "sha512") == expected


class TestValidateAlgorithm:
    def test_accepts_sha256(self):
        validate_algorithm("sha256")

    def test_rejects_unknown_algorithm(self):
        with pytest.raises(ValueError, match="unsupported algorithm"):
            validate_algorithm("not-a-real-algorithm")


class TestHashLines:
    def test_hashes_each_line_with_default_sha256(self):
        plugin = HashLines()
        result = plugin.run(["hello", "world"])

        assert result == [
            hashlib.sha256(b"hello").hexdigest(),
            hashlib.sha256(b"world").hexdigest(),
        ]

    def test_uses_custom_algorithm_from_options(self):
        plugin = HashLines(options='{"algorithm": "md5"}')
        result = plugin.run(["test"])

        assert result == [hashlib.md5(b"test").hexdigest()]

    def test_uses_prefix_from_options(self):
        plugin = HashLines(options='{"prefix": "x-"}')
        result = plugin.run(["data"])

        assert result == [hashlib.sha256(b"x-data").hexdigest()]

    def test_uses_suffix_from_options(self):
        plugin = HashLines(options='{"suffix": "-end"}')
        result = plugin.run(["data"])

        assert result == [hashlib.sha256(b"data-end").hexdigest()]

    def test_uses_key_from_options(self):
        plugin = HashLines(options='{"key": "my-key"}')
        result = plugin.run(["payload"])

        assert result == [
            hmac.new(b"my-key", b"payload", "sha256").hexdigest(),
        ]

    def test_preserves_empty_lines(self):
        plugin = HashLines()
        result = plugin.run(["a", "", "b"])

        assert result[0] == hashlib.sha256(b"a").hexdigest()
        assert result[1] == ""
        assert result[2] == hashlib.sha256(b"b").hexdigest()

    def test_invalid_algorithm_returns_error(self):
        plugin = HashLines(options='{"algorithm": "bad"}')
        result = plugin.run(["a", "", "b"])

        assert result == [
            format_error("unsupported algorithm: bad"),
        ]
