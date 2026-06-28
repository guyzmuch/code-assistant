from app.version import __version__


def test_version_is_non_empty_string():
    assert isinstance(__version__, str)
    assert __version__.strip()
