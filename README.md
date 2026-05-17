# Code Assistant

A desktop app to help in text/data transforming on input from the UI or clipboard.

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

For development (running tests), also install dev dependencies:

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
python main.py
```

## Run tests

With the virtual environment activated and dev dependencies installed:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

Run a single test file:

```bash
pytest tests/utils/test_format.py
```

Tests live under `tests/` and mirror the `plugins/` and `utils/` layout. Configuration is in `pyproject.toml`.
