import time

import pytest


@pytest.fixture(autouse=True)
def utc_timezone(monkeypatch):
    """Pin local timezone so fromtimestamp() matches fixed expected strings."""
    monkeypatch.setenv("TZ", "UTC")
    if hasattr(time, "tzset"):
        time.tzset()
