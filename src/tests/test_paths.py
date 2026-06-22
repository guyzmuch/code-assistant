import sys
from pathlib import Path

import paths


def test_bundle_root_points_to_src_in_dev_mode(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert paths.bundle_root() == Path(__file__).resolve().parent.parent


def test_user_data_dir_points_to_src_in_dev_mode(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert paths.user_data_dir() == Path(__file__).resolve().parent.parent


def test_user_data_dir_creates_directory(tmp_path, monkeypatch):
    data_dir = tmp_path / "user-data"

    def _user_data_dir():
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    monkeypatch.setattr(paths, "user_data_dir", _user_data_dir)
    assert paths.user_data_dir() == data_dir
    assert data_dir.is_dir()
