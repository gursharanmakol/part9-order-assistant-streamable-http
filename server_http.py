import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

logging.getLogger("mcp").setLevel(logging.WARNING)

load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

app = FastMCP(name="order-assistant", host=HOST, port=PORT, log_level="WARNING")


# ---------------------------------------------------------------------------
# Data helpers — unchanged from the low-level version
# ---------------------------------------------------------------------------

def _data_path() -> Path:
    base_dir = Path(__file__).resolve().parent
    raw = os.getenv("DATA_PATH", "./data/orders.json")
    p = Path(raw)
    if not p.is_absolute():
        p = base_dir / p
    return p.resolve()


def _load_orders() -> dict[str, Any]:
    path = _data_path()
    if not path.exists():
        return {"orders": []}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "orders" not in data:
        return {"orders": []}
    return data


def _save_orders(data: dict[str, Any]) -> None:
    path = _data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _find_order(data: dict[str, Any], order_id: str) -> dict[str, Any] | None:
    for o in data.get("orders", []):
        if isinstance(o, dict) and o.get("id") == order_id:
            return o
    return None


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@app.tool(
    title="Order Status Lookup",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_order_status(order_id: str) -> dict:
    """
    Retrieve the current status and shipping information for a customer order.
    Use this when the user asks about a specific order by ID, order number, or reference code.
    Returns status, carrier, and estimated delivery date.
    Do not use this for general product availability questions.
    """
    if not order_id.strip():
        return {"error": "invalid_arguments", "message": "Expected a non-empty string argument: order_id"}
    order_id = order_id.strip()

    data = _load_orders()
    order = _find_order(data, order_id)
    if order is None:
        return {"error": "not_found", "message": f"Order '{order_id}' was not found.", "order_id": order_id}

    return {
        "order_id": order_id,
        "status": order.get("status"),
        "carrier": order.get("carrier"),
        "delivery_estimate": order.get("delivery_estimate"),
    }


@app.tool(
    title="Order Line Items",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_order_items(order_id: str) -> dict:
    """
    Return the line items for a specific order. Use this when the user asks what is in an order
    or wants a breakdown of products. Returns a list of items with name, quantity, and unit price.
    """
    if not order_id.strip():
        return {"error": "invalid_arguments", "message": "Expected a non-empty string argument: order_id"}
    order_id = order_id.strip()

    data = _load_orders()
    order = _find_order(data, order_id)
    if order is None:
        return {"error": "not_found", "message": f"Order '{order_id}' was not found.", "order_id": order_id}

    return {
        "order_id": order_id,
        "items": order.get("items", []),
    }


@app.tool(
    title="Cancel Order",
    annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False),
)
async def cancel_order(order_id: str) -> dict:
    """
    Cancel a customer order. This action is irreversible. Confirm with the user before invoking.
    Do not call this tool based on an ambiguous request.
    """
    if not order_id.strip():
        return {"error": "invalid_arguments", "message": "Expected a non-empty string argument: order_id"}
    order_id = order_id.strip()

    data = _load_orders()
    order = _find_order(data, order_id)
    if order is None:
        return {"error": "not_found", "message": f"Order '{order_id}' was not found.", "order_id": order_id}

    if order.get("cancelled") is True or order.get("status") == "cancelled":
        return {"order_id": order_id, "cancelled": True, "message": "Order was already cancelled."}

    order["cancelled"] = True
    order["status"] = "cancelled"
    _save_orders(data)
    return {"order_id": order_id, "cancelled": True, "message": "Order cancelled successfully."}


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@app.resource(
    "recent-orders://summary",
    name="recent_orders_summary",
    title="Recent Orders (Summary)",
    description=(
        "Snapshot of the 10 most recent orders. "
        "Note: uses hyphens not underscores in the URI scheme because the MCP SDK validates URIs as URLs "
        "and underscores are not allowed in URL schemes."
    ),
)
async def recent_orders_summary() -> str:
    data = _load_orders()
    orders = list(data.get("orders", []))
    orders.sort(key=lambda o: o.get("created_at", ""), reverse=True)
    summary = [
        {"id": o.get("id"), "status": o.get("status"), "created_at": o.get("created_at")}
        for o in orders[:10]
    ]
    return json.dumps(summary, indent=2, sort_keys=True)


@app.resource(
    "order://{id}",
    name="order_by_id",
    title="Order by ID",
    description="Full order record for a given order ID",
)
async def order_by_id(id: str) -> str:
    data = _load_orders()
    order = _find_order(data, id)
    if order is None:
        payload: dict[str, Any] = {
            "error": "not_found",
            "message": f"Order '{id}' was not found.",
            "order_id": id,
        }
    else:
        payload = order
    return json.dumps(payload, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

@app.prompt(
    title="Summarize Order",
    description="Ask for a structured order summary for a given order.",
)
async def summarize_order(order_id: str) -> str:
    return (
        f"Provide a structured summary for order {order_id}.\n"
        "Return JSON with fields: order_id, status, carrier, delivery_estimate, cancelled, item_count, total_amount.\n"
        "Use the available tools/resources to retrieve the facts."
    )


@app.prompt(
    title="Customer-Friendly Response",
    description="Ask for a customer-facing support response for a given order.",
)
async def customer_friendly_response(order_id: str) -> str:
    return (
        f"Write a short, customer-friendly support response about order {order_id}.\n"
        "Be clear and empathetic. Mention status, carrier, and delivery estimate if available.\n"
        "Do not invent information; use tools/resources to look it up."
    )


# ---------------------------------------------------------------------------
# Entry point — Streamable HTTP transport (Part 9)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Starting order-assistant MCP server (Streamable HTTP)...")
    print(f"Endpoint: http://{HOST}:{PORT}{app.settings.streamable_http_path}", flush=True)
    app.run(transport="streamable-http")
