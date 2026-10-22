import json
import os
import sys
from pathlib import Path
from typing import Any

import anyio
from dotenv import load_dotenv

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters


load_dotenv()

# On Windows, the default console encoding may be cp1252; force UTF-8 so the
# article-friendly output renders consistently (punctuation and arrows).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)


def _capability_summary(capabilities: Any) -> str:
    caps = []
    if getattr(capabilities, "tools", None) is not None:
        caps.append("tools")
    if getattr(capabilities, "resources", None) is not None:
        caps.append("resources")
    if getattr(capabilities, "prompts", None) is not None:
        caps.append("prompts")
    return ", ".join(caps) if caps else "(none)"


async def main() -> None:
    base_dir = Path(__file__).resolve().parent

    print("=== MCP Order Assistant - Part 9 Demo (stdio) ===\n")

    server_env = os.environ.copy()
    server_env.setdefault("DATA_PATH", "./data/orders.json")
    server_env["PYTHONUNBUFFERED"] = "1"

    params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        cwd=str(base_dir),
        env=server_env,
    )

    print("[STEP 1] Connecting and discovering the server...")
    print("Connecting to order-assistant MCP server...")

    async with Client(params) as client:
        print(f"Protocol version: {client.protocol_version}")
        server_info = client.server_info
        server_label = server_info.name
        if getattr(server_info, "version", None):
            server_label = f"{server_label} v{server_info.version}"
        print(f"Server: {server_label}")
        print(f"Capabilities: {_capability_summary(client.server_capabilities)}\n")

        print("[STEP 2] Listing tools, resources and prompts...")

        tools_result = await client.list_tools()
        resources_result = await client.list_resources()
        templates_result = await client.list_resource_templates()
        prompts_result = await client.list_prompts()

        print("Tools:\n")
        for t in tools_result.tools:
            title = t.title or ""
            if title:
                print(f"- {t.name} ({title})")
            else:
                print(f"- {t.name}")

        print("\nResources:")
        for r in resources_result.resources:
            print(f"- {r.uri}")
        for rt in templates_result.resource_templates:
            print(f"- {rt.uri_template}")

        print("\nPrompts:")
        for p in prompts_result.prompts:
            print(f"- {p.name}")

        print("\n[STEP 3] Invoking tools...\n")

        async def call_and_print(tool_name: str, order_id: str) -> None:
            result = await client.call_tool(tool_name, {"order_id": order_id})
            payload = result.structured_content
            if payload is None and result.content:
                raw = getattr(result.content[0], "text", None)
                if raw:
                    try:
                        payload = json.loads(raw)
                    except json.JSONDecodeError:
                        payload = {"text": raw}
            if payload is None:
                payload = {"is_error": result.is_error}
            print(f"{tool_name}({order_id}): {_pretty(payload)}\n")

        await call_and_print("get_order_status", "ORD-10042")
        await call_and_print("get_order_items", "ORD-10042")
        await call_and_print("cancel_order", "ORD-10099")

    print("Interaction complete. Discover, list, call demonstrated.")


if __name__ == "__main__":
    anyio.run(main)
