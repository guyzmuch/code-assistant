from utils.format import format_section


def test_format_section_returns_header_line():
    assert format_section("HEADER") == "--- HEADER"
