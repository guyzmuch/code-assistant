import os
import sys
from pathlib import Path

APP_SLUG = "code-assistant"


def bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def user_data_dir() -> Path:
    if not getattr(sys, "frozen", False):
        path = Path(__file__).resolve().parent
    elif sys.platform == "win32":
        path = Path.home() / "AppData" / "Local" / "Code Assistant"
    else:
        config_home = os.environ.get("XDG_CONFIG_HOME")
        base = Path(config_home) if config_home else Path.home() / ".config"
        path = base / APP_SLUG
    path.mkdir(parents=True, exist_ok=True)
    return path


SRC_ROOT = bundle_root()
USER_DATA_DIR = user_data_dir()
