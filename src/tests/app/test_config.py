import json

import pytest

from app import config


@pytest.fixture
def config_path(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr(config, "CONFIG_PATH", path)
    return path


def test_load_app_config_returns_defaults_when_file_missing(config_path):
    assert config.load_app_config() == config.DEFAULT_CONFIG


def test_save_and_load_round_trip(config_path):
    data = {"text_font_size": 14, "history_open_at_startup": True}
    config.save_app_config(data)

    loaded = config.load_app_config()
    assert loaded["text_font_size"] == 14
    assert loaded["history_open_at_startup"] is True


def test_load_app_config_merges_partial_file(config_path):
    config_path.write_text(json.dumps({"text_font_size": 12}), encoding="utf-8")

    loaded = config.load_app_config()
    assert loaded["text_font_size"] == 12
    assert loaded["history_open_at_startup"] is False


def test_convenience_setters(config_path):
    config.set_text_font_size(16)
    config.set_history_open_at_startup(True)

    assert config.get_text_font_size() == 16
    assert config.get_history_open_at_startup() is True
