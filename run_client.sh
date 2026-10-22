#!/usr/bin/env bash
# NOTE: This file must use LF line endings (not CRLF) for bash.
# Run this in a second terminal AFTER the server is running.
set -euo pipefail

cd "$(dirname "$0")"

echo "Running Streamable HTTP client..."
uv run --locked python client_http.py
