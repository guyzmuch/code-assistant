from pathlib import Path

from app.branding import PROCESS_NAME, WM_CLASS, app_icon_path


def test_app_icon_exists():
    path = app_icon_path()
    assert path is not None
    assert path.is_file()


def test_app_icon_is_png():
    path = app_icon_path()
    assert path is not None
    assert path.suffix == ".png"


def test_process_name_is_short_enough_for_linux_prctl():
    assert len(PROCESS_NAME.encode()) <= 15


def test_wm_class_matches_window_title_brand():
    assert WM_CLASS == "DevToolbelt"
