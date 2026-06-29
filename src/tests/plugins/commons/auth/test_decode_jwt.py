from plugins.commons.auth.decode_jwt import DecodeJwt

# header: {"alg":"HS256","typ":"JWT"}  payload: {"sub":"1234567890"}
SAMPLE_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
    "signature"
)

# payload: {"sub":"user","exp":1778803200,"delivery":1355270400}
TIMESTAMP_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzc4ODAzMjAwLCJkZWxpdmVyeSI6MTM1NTI3MDQwMH0."
    "signature"
)

EXPECTED_HEADER_JSON = """{
  "alg": "HS256",
  "typ": "JWT"
}"""

EXPECTED_PAYLOAD_JSON = """{
  "sub": "1234567890"
}"""


class TestDecodeJwt:
    def test_decodes_header_and_payload_json(self):
        plugin = DecodeJwt()
        result = plugin.run([SAMPLE_JWT])[0]

        _, after_header = result.split("--- HEADER\n", 1)
        header_json, payload_json = after_header.split("\n--- PAYLOAD\n", 1)

        assert header_json == EXPECTED_HEADER_JSON
        assert payload_json == EXPECTED_PAYLOAD_JSON

    def test_decodes_header_and_payload(self):
        plugin = DecodeJwt()
        result = plugin.run([SAMPLE_JWT])[0]

        assert "--- HEADER" in result
        assert '"alg": "HS256"' in result
        assert '"typ": "JWT"' in result
        assert "--- PAYLOAD" in result
        assert '"sub": "1234567890"' in result

    def test_strips_bearer_prefix(self):
        plugin = DecodeJwt()
        result = plugin.run([f"Bearer {SAMPLE_JWT}"])[0]

        assert '"sub": "1234567890"' in result

    def test_empty_input_returns_error(self):
        plugin = DecodeJwt()
        result = plugin.run([])[0]

        assert "--- ERROR" in result
        assert "no input provided" in result

    def test_empty_lines_return_error(self):
        plugin = DecodeJwt()
        result = plugin.run(["   "])[0]

        assert "--- ERROR" in result
        assert "no non-empty line found" in result

    def test_uses_first_non_empty_line(self):
        plugin = DecodeJwt()
        result = plugin.run(["", "  ", SAMPLE_JWT])[0]

        assert '"sub": "1234567890"' in result

    def test_invalid_token_returns_error(self):
        plugin = DecodeJwt()
        result = plugin.run(["not-a-jwt"])[0]

        assert "--- ERROR" in result
        assert "Invalid JWT" in result

    def test_payload_only_returns_payload_without_sections(self):
        plugin = DecodeJwt(options='{"payload_only": true}')
        result = plugin.run([SAMPLE_JWT])[0]

        assert result == EXPECTED_PAYLOAD_JSON
        assert "--- HEADER" not in result
        assert "--- PAYLOAD" not in result

    def test_compact_json_when_pretty_disabled(self):
        plugin = DecodeJwt(options='{"pretty": false}')
        result = plugin.run([SAMPLE_JWT])[0]

        assert result.split("\n--- PAYLOAD\n", 1)[1] == '{"sub":"1234567890"}'
        assert "\n  " not in result

    def test_extra_data_section_converts_timestamps(self, bogota_timezone):
        plugin = DecodeJwt()
        result = plugin.run([TIMESTAMP_JWT])[0]

        assert "--- EXTRA DATA" in result
        assert "exp: 2026-05-14 19:00:00" in result
        assert "delivery: 2012-12-11 19:00:00" in result

    def test_extra_data_omitted_when_no_timestamps(self):
        plugin = DecodeJwt()
        result = plugin.run([SAMPLE_JWT])[0]

        assert "--- EXTRA DATA" not in result

    def test_payload_only_excludes_extra_data(self, bogota_timezone):
        plugin = DecodeJwt(options='{"payload_only": true}')
        result = plugin.run([TIMESTAMP_JWT])[0]

        assert "--- EXTRA DATA" not in result
        assert "exp:" not in result
