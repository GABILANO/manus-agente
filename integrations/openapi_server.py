"""Small OpenAPI-compatible HTTP adapter for non-MCP AI clients."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai

app = FastAPI(title="Managed Agent Tool", version="1.0.0")
_agent_name = os.getenv("MANAGED_AGENT", "antigravity-preview-05-2026")
_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise RuntimeError("GEMINI_API_KEY is required")
client = genai.Client(api_key=_api_key)


class RunRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=100_000)
    agent: str | None = None
    environment_id: str | None = None
    previous_interaction_id: str | None = None


class RunResponse(BaseModel):
    output: str
    interaction_id: str | None = None
    environment_id: str | None = None
    status: str | None = None


@app.post("/v1/managed-agent/run", response_model=RunResponse)
def run_managed_agent(request: RunRequest) -> RunResponse:
    kwargs: dict[str, Any] = {
        "agent": request.agent or _agent_name,
        "input": request.input,
        "environment": request.environment_id or "remote",
    }
    if request.previous_interaction_id:
        kwargs["previous_interaction_id"] = request.previous_interaction_id
    try:
        interaction = client.interactions.create(**kwargs)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Managed agent request failed") from exc
    return RunResponse(
        output=interaction.output_text,
        interaction_id=interaction.id,
        environment_id=interaction.environment_id,
        status=interaction.status,
    )
