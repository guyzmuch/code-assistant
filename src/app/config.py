import json
import os
import tempfile

from paths import USER_DATA_DIR

CONFIG_PATH = USER_DATA_DIR / "config.json"

DEFAULT_CONFIG = {
    "text_font_size": 10,
    "history_open_at_startup": False,
}


def load_app_config():
    if not CONFIG_PATH.exists():
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_PATH, encoding="utf-8") as config_file:
        data = json.load(config_file)
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def save_app_config(config):
    merged = dict(DEFAULT_CONFIG)
    merged.update(config)
    fd, tmp_path = tempfile.mkstemp(dir=str(CONFIG_PATH.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            json.dump(merged, tmp_file, indent=2)
            tmp_file.write("\n")
        os.replace(tmp_path, CONFIG_PATH)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def get_text_font_size():
    return load_app_config()["text_font_size"]


def set_text_font_size(size):
    config = load_app_config()
    config["text_font_size"] = size
    save_app_config(config)


def get_history_open_at_startup():
    return load_app_config()["history_open_at_startup"]


def set_history_open_at_startup(enabled):
    config = load_app_config()
    config["history_open_at_startup"] = enabled
    save_app_config(config)
