import json
import os
import sys
from pathlib import Path
from typing import Any

import anyio
from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


load_dotenv()

# On Windows, the default console encoding may be cp1252; force UTF-8 so the
# article-friendly output renders consistently (e.g., em-dash and arrows).
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

    print("=== MCP Order Assistant — Part 5 Demo ===\n")

    server_env = os.environ.copy()
    server_env.setdefault("DATA_PATH", "./data/orders.json")
    server_env["PYTHONUNBUFFERED"] = "1"

    params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        cwd=str(base_dir),
        env=server_env,
    )

    print("[STEP 1] Initializing...")
    print("Connecting to order-assistant MCP server...")

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            init = await session.initialize()

            print(f"Protocol version: {init.protocolVersion}")
            server_info = init.serverInfo
            server_label = server_info.name
            if getattr(server_info, "version", None):
                server_label = f"{server_label} v{server_info.version}"
            print(f"Server: {server_label}")
            print(f"Capabilities: {_capability_summary(init.capabilities)}\n")

            print("[STEP 2] Discovering capabilities...")

            tools_result = await session.list_tools()
            resources_result = await session.list_resources()
            templates_result = await session.list_resource_templates()
            prompts_result = await session.list_prompts()

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
            for rt in templates_result.resourceTemplates:
                print(f"- {rt.uriTemplate}")

            print("\nPrompts:")
            for p in prompts_result.prompts:
                print(f"- {p.name}")

            print("\n[STEP 3] Invoking tools...\n")

            async def call_and_print(tool_name: str, order_id: str) -> None:
                result = await session.call_tool(tool_name, {"order_id": order_id})
                payload = result.structuredContent
                if payload is None and result.content:
                    # FastMCP serialises the return value as JSON text in content[0].
                    # Parse it back so we print clean JSON, not SDK object repr.
                    raw = getattr(result.content[0], "text", None)
                    if raw:
                        try:
                            payload = json.loads(raw)
                        except json.JSONDecodeError:
                            payload = {"text": raw}
                if payload is None:
                    payload = {"isError": result.isError}
                print(f"{tool_name}({order_id}): {_pretty(payload)}\n")

            await call_and_print("get_order_status", "ORD-10042")
            await call_and_print("get_order_items", "ORD-10042")
            await call_and_print("cancel_order", "ORD-10099")

    print("Interaction complete. initialize \u2192 list \u2192 call pattern demonstrated.")


if __name__ == "__main__":
    anyio.run(main)
