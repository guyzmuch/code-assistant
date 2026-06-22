#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -d venv ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

pip install -q -r requirements.txt -r requirements-dev.txt

pyinstaller code-assistant.spec --noconfirm

if [[ -f dist/code-assistant.exe ]]; then
  echo "Built: dist/code-assistant.exe"
elif [[ -d dist/code-assistant.app ]]; then
  echo "Built: dist/code-assistant.app"
else
  echo "Built: dist/code-assistant"
fi
