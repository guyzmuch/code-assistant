import time

import pytest


@pytest.fixture(autouse=True)
def bogota_timezone(monkeypatch):
    """Pin local timezone so fromtimestamp() matches fixed expected strings."""
    monkeypatch.setenv("TZ", "America/Bogota")
    if hasattr(time, "tzset"):
        time.tzset()
