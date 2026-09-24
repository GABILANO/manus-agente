"""MCP adapter for the managed agent in the quickstart notebook.

Run with:
    GEMINI_API_KEY=... python integrations/managed_agent_mcp_server.py

The server uses stdio, which is the portable MCP transport for local AI clients.
"""

from __future__ import annotations

import json
import os
from typing import Any

from google import genai
from mcp.server.fastmcp import FastMCP

DEFAULT_AGENT = os.getenv("MANAGED_AGENT", "antigravity-preview-05-2026")
_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise RuntimeError("GEMINI_API_KEY is required")

client = genai.Client(api_key=_api_key)
mcp = FastMCP("managed-agents")


def _run(
    input: str,
    agent: str = DEFAULT_AGENT,
    environment_id: str | None = None,
    previous_interaction_id: str | None = None,
) -> str:
    environment: Any = environment_id or "remote"
    kwargs: dict[str, Any] = {
        "agent": agent,
        "input": input,
        "environment": environment,
    }
    if previous_interaction_id:
        kwargs["previous_interaction_id"] = previous_interaction_id

    interaction = client.interactions.create(**kwargs)
    return json.dumps(
        {
            "output": interaction.output_text,
            "interaction_id": interaction.id,
            "environment_id": interaction.environment_id,
            "status": interaction.status,
        },
        ensure_ascii=False,
    )


@mcp.tool()
def run_managed_agent(
    input: str,
    agent: str = DEFAULT_AGENT,
) -> str:
    """Run a managed agent for an autonomous task.

    Use this for research, code execution, file work, and multi-step tasks.
    The returned IDs can be supplied to continue the same task.
    """
    return _run(input=input, agent=agent)


@mcp.tool()
def continue_managed_agent(
    input: str,
    environment_id: str,
    previous_interaction_id: str | None = None,
    agent: str = DEFAULT_AGENT,
) -> str:
    """Continue a task in an existing managed-agent sandbox."""
    return _run(
        input=input,
        agent=agent,
        environment_id=environment_id,
        previous_interaction_id=previous_interaction_id,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
