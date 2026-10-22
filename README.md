# MCP Order Assistant - Part 9 (Streamable HTTP)

Verified with MCP revision 2026-07-28 and the Python SDK mcp 2.3.0.

Need the earlier 2025-11-25 version of this lab? Check out the tag `mcp-baseline-pre-2026-07-28`.

The same TechNova order assistant from Part 5, moved from **stdio** to **Streamable HTTP** transport. The tools, resources, prompts, and protocol flow are identical. Only the transport changed.

This example runs on localhost to demonstrate the transition from stdio to Streamable HTTP. It is not a production deployment.

Authentication, authorization, and other production security controls are intentionally out of scope for this lab; MCP Parts 6-8 cover those concerns.

## Prerequisites

- Python **3.11+** (default local version is 3.12 via `.python-version`)
- [uv](https://docs.astral.sh/uv/) for the recommended workflow
- A bash shell to run the `.sh` scripts (macOS/Linux Terminal, or Git Bash / WSL on Windows)

`uv.lock` provides the reproducible environment for this lab.

Note: on Windows, `mcp` may pull in `pywin32` automatically as a transitive dependency.

### Windows users

The `.sh` scripts require a bash shell. The easiest setup is often to open the repo in VS Code and set the integrated terminal to Git Bash or WSL. Options:

- **Git Bash** (recommended): install [Git for Windows](https://git-scm.com/download/win), open Git Bash, then run `bash run_server.sh` and `bash run_client.sh`
- **WSL**: open a WSL terminal, then run the same commands
- **Manual uv commands** (no bash needed): see below

## Project Structure

```
part9-order-assistant-streamable-http/
├── server.py              # stdio server (same tools as Part 5)
├── client.py              # stdio client
├── server_http.py         # Streamable HTTP server
├── client_http.py         # Streamable HTTP client
├── seed_data.py           # Data seeder
├── pyproject.toml         # Direct dependencies (source of truth)
├── uv.lock                # Locked reproducible environment
├── requirements.txt       # Generated pip compatibility artifact
├── data/
│   └── orders.json        # Seeded order data
├── images/
│   └── mcp-inspector-streamable-http.png
├── run_server.sh          # Seed + start HTTP server via uv
├── run_client.sh          # Run HTTP client via uv
├── .env.example           # Environment config example
└── README.md
```

To keep the transition from Part 5 easy to compare, this example keeps separate stdio and Streamable HTTP server files instead of refactoring shared logic into a common module.

## Run (recommended: uv)

Unlike Part 5 (where the client launched the server as a subprocess), Part 9 uses HTTP. The server runs in its own terminal and the client connects to it over the network.

First sync once:

```bash
uv sync --locked
```

### Terminal 1 - Start the server

```bash
bash run_server.sh
```

Or:

```bash
uv run --locked python seed_data.py
uv run --locked python server_http.py
```

This seeds `./data/orders.json` and starts the Streamable HTTP server on `http://127.0.0.1:8000/mcp`.

Leave this running.

### Terminal 2 - Run the client

```bash
bash run_client.sh
```

Or:

```bash
uv run --locked python client_http.py
```

Note: `cancel_order` intentionally modifies `data/orders.json`. Re-run the server script (or re-seed) to reset state.

### Pip fallback (without uv)

`requirements.txt` is generated from `uv.lock`. Do not edit it by hand. If you change dependencies, edit `pyproject.toml`, run `uv lock`, then regenerate with `uv export`.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python seed_data.py
python server_http.py       # Terminal 1
python client_http.py       # Terminal 2
```

## What you'll see

Terminal output from a successful HTTP client run looks like this:

```text
=== MCP Order Assistant - Part 9 Demo (Streamable HTTP) ===

[STEP 1] Connecting and discovering the server...
Connecting to order-assistant MCP server at http://127.0.0.1:8000/mcp...
Protocol version: 2026-07-28
Server: order-assistant
Capabilities: tools, resources, prompts

[STEP 2] Listing tools, resources and prompts...
Tools:

- get_order_status (Order Status Lookup)
- get_order_items (Order Line Items)
- cancel_order (Cancel Order)

Resources:
- recent-orders://summary
- order://{id}

Prompts:
- summarize_order
- customer_friendly_response

[STEP 3] Invoking tools...

get_order_status(ORD-10042): {
  "carrier": "FedEx",
  "delivery_estimate": "2026-03-28",
  "order_id": "ORD-10042",
  "status": "shipped"
}

get_order_items(ORD-10042): {
  "items": [
    {
      "name": "Wireless Headphones",
      "price": 79.99,
      "quantity": 1
    },
    {
      "name": "Phone Case",
      "price": 12.99,
      "quantity": 2
    }
  ],
  "order_id": "ORD-10042"
}

cancel_order(ORD-10099): {
  "cancelled": true,
  "message": "Order cancelled successfully.",
  "order_id": "ORD-10099"
}

get_order_status(ORD-10099): {
  "carrier": "UPS",
  "delivery_estimate": "2026-03-30",
  "order_id": "ORD-10099",
  "status": "cancelled"
}

Interaction complete. Discover, list, call demonstrated.
```

The four tool calls are:

- `get_order_status("ORD-10042")` - lookup a shipped order
- `get_order_items("ORD-10042")` - get line items
- `cancel_order("ORD-10099")` - cancel a processing order
- `get_order_status("ORD-10099")` - confirm cancellation took effect

## Configuration

The server reads `DATA_PATH` from environment, defaulting to `./data/orders.json`.

An example env file is included:

- Copy `.env.example` to `.env` if you want to customize the data path.

## Endpoint Details

| Setting | Value | Source |
|---------|-------|--------|
| Host | `127.0.0.1` | Lab default (`HOST`) |
| Port | `8000` | Lab default (`PORT`) |
| Path | `/mcp` | Streamable HTTP path used by this lab |
| Full URL | **`http://127.0.0.1:8000/mcp`** | Combined |

## Validate with MCP Inspector (optional)

With the server running, you can use MCP Inspector to verify the endpoint and browse its tools, resources, and prompts interactively.

In another terminal:

```bash
npx @modelcontextprotocol/inspector
```

This opens the Inspector UI in your browser. To connect:

1. Set **Transport Type** to **Streamable HTTP**
2. Enter `http://127.0.0.1:8000/mcp` as the URL
3. Click **Connect**

If the connection succeeds, you'll see the three TechNova tools - Order Status Lookup, Order Line Items, and Cancel Order - listed in the Tools tab.

![MCP Inspector connected to the Streamable HTTP server, showing the three order-assistant tools](images/mcp-inspector-streamable-http.png)
*MCP Inspector connected over Streamable HTTP and listing the TechNova tools.*

## What Changed from Part 5

### Server (`server_http.py` vs `server.py`)

| Aspect | Part 5 / stdio | Part 9 HTTP |
|--------|----------------|-------------|
| Transport | `app.run(transport="stdio")` | `app.run(transport="streamable-http", host=..., port=...)` |
| Startup | Launched as subprocess by client | Runs as HTTP service on `127.0.0.1:8000` |
| Endpoint | stdin/stdout | `http://127.0.0.1:8000/mcp` |

Everything else - tools, resources, prompts, data helpers - is **identical**.

### Client (`client_http.py` vs `client.py`)

| Aspect | stdio client | HTTP client |
|--------|--------------|-------------|
| Construction | `Client(StdioServerParameters(...))` | `Client("http://127.0.0.1:8000/mcp")` |
| Connection | Launches server subprocess | Connects to a running server |
| Demo flow | connect, list, call tools | connect, list, call tools (same shape) |

### Dependencies

Both transports use the same `mcp==2.3.0` dependency set from `pyproject.toml` / `uv.lock`.

## Derived fields in prompts

The `summarize_order` prompt asks for fields like `item_count` and `total_amount`. These aren't stored directly in the JSON; they're meant to be derived from the order's `items`.

## Running the stdio Demo

The stdio files still work independently:

```bash
uv run --locked python seed_data.py
uv run --locked python client.py
```

The stdio client launches the server as a subprocess - no separate terminal needed.

## Companion Article

This repository accompanies
[Part 9: From Concepts to a Hands-On Example](https://aiinpracticehub.com/articles/from-concepts-to-a-hands-on-example/)
in the
[MCP in Practice series](https://aiinpracticehub.com/series/mcp/)
on [AI in Practice Hub](https://aiinpracticehub.com/).

## What This Example Shows

A developer who built the Part 5 stdio version should look at the diff and think:

> "The tools are identical. Only the transport changed."

The same applies to the client:

> "The discovery and tool-call flow is identical. Only the connection method changed."

The protocol stays the same. Only the transport changes.
