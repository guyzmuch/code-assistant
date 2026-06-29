import ctypes
import sys
import tkinter as tk
from pathlib import Path

from paths import bundle_root

WINDOW_TITLE = "DevToolbelt"
PROCESS_NAME = "dev-toolbelt"
WM_CLASS = "DevToolbelt"

_ICON_PATHS = (
    bundle_root() / "assets" / "icon.png",
    bundle_root().parent / "assets" / "icon.png",
)


def app_icon_path() -> Path | None:
    for path in _ICON_PATHS:
        if path.is_file():
            return path
    return None


def set_process_name(name: str = PROCESS_NAME) -> None:
    encoded = name.encode()

    if sys.platform == "darwin":
        try:
            libc = ctypes.CDLL(None)
            if hasattr(libc, "setprogname"):
                libc.setprogname(encoded)
        except Exception:
            pass
        return

    if sys.platform.startswith("linux"):
        try:
            libc = ctypes.CDLL(None)
            PR_SET_NAME = 15
            libc.prctl(PR_SET_NAME, encoded[:15], 0, 0, 0)
        except Exception:
            pass


def apply_window_branding(root: tk.Misc) -> None:
    icon_path = app_icon_path()
    if icon_path is not None:
        icon_image = tk.PhotoImage(file=str(icon_path))
        root.iconphoto(True, icon_image)
        root._icon_image_ref = icon_image  # prevent garbage collection

    if sys.platform.startswith("linux"):
        try:
            root.tk.call("wm", "class", root._w, WM_CLASS, WM_CLASS)
        except tk.TclError:
            pass
