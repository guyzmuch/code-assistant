# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

sys.path.insert(0, str(Path(SPECPATH) / "src"))

_version_ns = {}
exec(
    (Path(SPECPATH) / "src" / "app" / "version.py").read_text(encoding="utf-8"),
    _version_ns,
)
APP_VERSION = _version_ns["__version__"]


def _version_tuple(version):
    parts = [int(part) for part in version.split(".")]
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])


def _windows_version_file(version):
    version_tuple = _version_tuple(version)
    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u'DevToolbelt'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'dev-toolbelt'),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', u'dev-toolbelt.exe'),
        StringStruct(u'ProductName', u'DevToolbelt'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    path = Path(SPECPATH) / "build" / "version_info.txt"
    path.parent.mkdir(exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


block_cipher = None

hiddenimports = collect_submodules("plugins")
hiddenimports += [
    "tkinterdnd2",
    "pyperclip",
]

a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe_kwargs = {
    "debug": False,
    "bootloader_ignore_signals": False,
    "strip": False,
    "upx": True,
    "upx_exclude": [],
    "runtime_tmpdir": None,
    "console": False,
    "disable_windowed_traceback": False,
    "argv_emulation": False,
    "target_arch": None,
    "codesign_identity": None,
    "entitlements_file": None,
}
if sys.platform == "win32":
    exe_kwargs["version"] = str(_windows_version_file(APP_VERSION))

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="dev-toolbelt",
    **exe_kwargs,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="DevToolbelt.app",
        icon=None,
        bundle_identifier="dev.toolbelt",
        info_plist={
            "CFBundleDisplayName": "DevToolbelt",
            "CFBundleShortVersionString": APP_VERSION,
            "CFBundleVersion": APP_VERSION,
        },
    )
