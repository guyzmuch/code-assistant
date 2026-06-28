#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -d venv ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

pip install -q -r requirements.txt -r requirements-dev.txt

pyinstaller dev-toolbelt.spec --noconfirm

if [[ -f dist/dev-toolbelt.exe ]]; then
  echo "Built: dist/dev-toolbelt.exe"
elif [[ -d dist/dev-toolbelt.app ]]; then
  echo "Built: dist/dev-toolbelt.app"
else
  echo "Built: dist/dev-toolbelt"
fi
