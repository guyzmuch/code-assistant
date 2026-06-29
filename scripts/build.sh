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

resolve_artifact() {
  if [[ -f dist/dev-toolbelt.exe ]]; then
    echo "dist/dev-toolbelt.exe"
  elif [[ -f dist/DevToolbelt.app/Contents/MacOS/dev-toolbelt ]]; then
    echo "dist/DevToolbelt.app/Contents/MacOS/dev-toolbelt"
  elif [[ -f dist/dev-toolbelt ]]; then
    echo "dist/dev-toolbelt"
  else
    return 1
  fi
}

write_checksums() {
  local artifact="$1"
  local name version sha256 built_at

  name="$(basename "$artifact")"
  version="$(PYTHONPATH=src python -c "from app.version import __version__; print(__version__)")"
  sha256="$(sha256sum "$artifact" | awk '{print $1}')"
  built_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  cat > dist/checksums.txt <<EOF
DevToolbelt ${version}
Built: ${built_at} UTC
Artifact: ${artifact}

SHA256: ${sha256}

Verify (Linux):
  cd dist && sha256sum -c SHA256SUMS
EOF

  printf '%s  %s\n' "$sha256" "$name" > dist/SHA256SUMS

  echo "Checksums: dist/checksums.txt"
  echo "  SHA256  ${sha256}"
}

artifact="$(resolve_artifact)"
echo "Built: ${artifact}"
write_checksums "$artifact"
