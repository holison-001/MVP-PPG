#!/usr/bin/env bash
# Validate and export the existing board. Never regenerate placement or reroute.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${KICAD_PYTHON:-}" ]]; then
    PYTHON="$KICAD_PYTHON"
elif [[ -n "${KICAD_BIN:-}" && -x "$KICAD_BIN/python.exe" ]]; then
    PYTHON="$KICAD_BIN/python.exe"
elif [[ -x "/c/Program Files/KiCad/10.0/bin/python.exe" ]]; then
    PYTHON="/c/Program Files/KiCad/10.0/bin/python.exe"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
else
    echo "Set KICAD_PYTHON to a Python executable with KiCad's pcbnew module." >&2
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/export_v08.py" "$@"
