from plugins.commons.auth.decode_jwt import DecodeJwt

# header: {"alg":"HS256","typ":"JWT"}  payload: {"sub":"1234567890"}
SAMPLE_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
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

    def test_empty_first_line_returns_error(self):
        plugin = DecodeJwt()
        result = plugin.run(["   "])[0]

        assert "--- ERROR" in result
        assert "first line is empty" in result

    def test_invalid_token_returns_error(self):
        plugin = DecodeJwt()
        result = plugin.run(["not-a-jwt"])[0]

        assert "--- ERROR" in result
        assert "Invalid JWT" in result
