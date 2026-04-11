#!/usr/bin/env bash
# NOTE: This file must use LF line endings (not CRLF) for bash.
# Run this in a second terminal AFTER the server is running.
set -euo pipefail

cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
  VENV_PY=".venv/bin/python"
else
  VENV_PY=".venv/Scripts/python.exe"
fi

if [ ! -x "$VENV_PY" ]; then
  echo "Error: .venv not found. Run 'bash run_server.sh' first to create it." >&2
  exit 1
fi

echo "Running Streamable HTTP client..."
"$VENV_PY" client_http.py
