# DevToolbelt

A desktop app of small developer utilities for transforming text and data from the UI or clipboard.

## Requirements

- Python 3.12+ (or a compatible 3.x version)
- Tkinter (usually included with Python on Linux; on Debian/Ubuntu you may need `sudo apt install python3-tk`)

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For development (running tests, building executables), also install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

## Run the app

From the project root, with the virtual environment activated:

```bash
./run.sh
```

Or directly:

```bash
source venv/bin/activate
PYTHONPATH=src python src/main.py
```

Settings and data file locations depend on how you run the app:

| Mode | `config.json` / `plugins.db` |
|------|------------------------------|
| Development (`./run.sh`) | `src/config.json`, `src/plugins.db` |
| Bundled executable | per-user directory (see below) |

Bundled app data directory:

| OS | Location |
|----|----------|
| Linux | `~/.config/dev-toolbelt/` |
| macOS | `~/.config/dev-toolbelt/` |
| Windows | `%LOCALAPPDATA%\DevToolbelt\` |

## Build an executable

The app is packaged with [PyInstaller](https://pyinstaller.org/) as a single-file executable. **Build on the target OS** — you cannot cross-compile a Linux binary on macOS (or the reverse).

### Quick build

From the project root:

```bash
./scripts/build.sh
```

This installs dev dependencies (including PyInstaller), runs the spec file, and writes output to `dist/`.

### Output by platform

| OS | Output |
|----|--------|
| Linux | `dist/dev-toolbelt` |
| macOS | `dist/dev-toolbelt` or `dist/dev-toolbelt.app` |
| Windows | `dist/dev-toolbelt.exe` |

Run the binary directly (Linux/macOS):

```bash
./dist/dev-toolbelt
```

On macOS, if you get a `.app` bundle, open it from Finder or run:

```bash
open dist/dev-toolbelt.app
```

### Manual build

```bash
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pyinstaller dev-toolbelt.spec --noconfirm
```

Configuration lives in `dev-toolbelt.spec` (one-file, windowed, plugins collected automatically).

### Notes

- When running the bundled app, user data is written to the per-user directory above (not inside the bundle).
- For distribution on macOS, you may need to codesign or notarize the app for Gatekeeper.
- Windows builds require running PyInstaller on Windows (or a Windows CI runner).

## Run tests

With the virtual environment activated and dev dependencies installed:

```bash
PYTHONPATH=src pytest src/tests
```

Verbose output:

```bash
PYTHONPATH=src pytest src/tests -v
```

Run a single test file:

```bash
PYTHONPATH=src pytest src/tests/utils/test_format.py
```

Tests live under `src/tests/`. Configuration is in `pyproject.toml`.
