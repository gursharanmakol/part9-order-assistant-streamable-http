#!/usr/bin/env bash
# NOTE: This file must use LF line endings (not CRLF) for bash.
set -euo pipefail

cd "$(dirname "$0")"

PY=""
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
  PY="python3"
elif command -v py >/dev/null 2>&1 && py -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
  PY="py"
elif command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
  PY="python"
else
  echo "Error: Python 3.10+ is required (python3, py, or python not found)." >&2
  exit 1
fi

if ! "$PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'; then
  echo "Error: Python 3.10+ is required. Found: $("$PY" -V 2>&1)" >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating local virtual environment (.venv)..."
  "$PY" -m venv .venv
  if [ -x ".venv/bin/python" ]; then
    VENV_PY=".venv/bin/python"
  else
    VENV_PY=".venv/Scripts/python.exe"
  fi
  echo "Installing dependencies into .venv..."
  "$VENV_PY" -m pip install --upgrade pip >/dev/null
  "$VENV_PY" -m pip install -r requirements.txt >/dev/null
else
  echo ".venv already exists — skipping install."
  if [ -x ".venv/bin/python" ]; then
    VENV_PY=".venv/bin/python"
  else
    VENV_PY=".venv/Scripts/python.exe"
  fi
fi

echo "Seeding local JSON data..."
"$VENV_PY" seed_data.py

echo "Starting Streamable HTTP server..."
"$VENV_PY" server_http.py
