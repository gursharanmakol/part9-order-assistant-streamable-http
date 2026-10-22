#!/usr/bin/env bash
# NOTE: This file must use LF line endings (not CRLF) for bash.
set -euo pipefail

cd "$(dirname "$0")"

echo "Seeding local JSON data..."
uv run --locked python seed_data.py

echo "Starting Streamable HTTP server..."
uv run --locked python server_http.py
