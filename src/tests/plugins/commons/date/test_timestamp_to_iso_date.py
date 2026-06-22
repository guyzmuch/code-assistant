from plugins.commons.date.timestamp_to_iso_date import TimestampToIsoDate

# Plugin uses datetime.fromtimestamp() (local time). Tests pin TZ=America/Bogota via conftest.
EXPECTED_ISO_0 = "1969-12-31T19:00:00"
EXPECTED_ISO_123456789 = "1973-11-29T16:33:09"


class TestTimestampToIsoDate:
    def test_converts_timestamp_to_iso(self):
        plugin = TimestampToIsoDate()
        result = plugin.run(["123456789"])

        assert result == [EXPECTED_ISO_123456789]

    def test_converts_multiple_lines(self):
        plugin = TimestampToIsoDate()
        result = plugin.run(["0", "123456789"])

        assert result == [EXPECTED_ISO_0, EXPECTED_ISO_123456789]

    def test_preserves_empty_lines(self):
        plugin = TimestampToIsoDate()
        result = plugin.run(["0", "", "123456789"])

        assert result == [EXPECTED_ISO_0, "", EXPECTED_ISO_123456789]

    def test_invalid_timestamp_returns_error(self):
        plugin = TimestampToIsoDate()
        result = plugin.run(["not-a-number"])

        assert result[0].startswith("Error:")

    def test_uses_configured_timezone(self):
        plugin = TimestampToIsoDate(options='{"timezone": "Europe/Paris"}')
        result = plugin.run(["123456789"])

        assert result == ["1973-11-29T22:33:09"]

    def test_shows_offset_when_hide_offset_disabled(self):
        plugin = TimestampToIsoDate(
            options='{"timezone": "Europe/Paris", "hide_offset": false}'
        )
        result = plugin.run(["123456789"])

        assert result == ["1973-11-29T22:33:09+01:00"]
