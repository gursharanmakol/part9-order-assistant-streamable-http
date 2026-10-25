# Wire captures

- Capture date: 2026-10-22
- Transport: streamable-http
- Capture method/tool: a temporary capture script with JSON-RPC dispatcher and HTTP header hooks, run against the final lab code (the script is not part of this repo)
- Python version: 3.12.9
- mcp version: 2.3.0
- MCP protocol revision: 2026-07-28

## Files

JSON request/response bodies for:

1. first exchange (`server/discover`)
2. `tools/list`
3. `tools/call` for `get_order_status` with `ORD-10042`

Values that can vary between runs include JSON-RPC request `id` values and any freshly generated tokens. Tool payloads for this seeded demo are otherwise stable after `seed_data.py`.

Do not treat these files as editable fixtures. Recapture from the final code if the protocol surface changes.

`http-headers.json` stores protocol-relevant HTTP headers only. Secret headers are never persisted.
