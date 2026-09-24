# Managed Agent interoperability

This directory exposes the managed agent as a reusable tool for AI clients instead of requiring every client to understand the Python notebook.

## Supported integration styles

| Client | Recommended adapter | Transport |
|---|---|---|
| Gemini CLI | MCP server | stdio |
| Manus AI | MCP server, when MCP tools are enabled | stdio or hosted MCP |
| Gemini web/AI Studio integrations | OpenAPI adapter | HTTP + JSON |
| Grok or any agent with HTTP tools | OpenAPI adapter | HTTP + JSON |
| Custom applications | Python SDK or either adapter | Python/MCP/HTTP |

MCP is the primary integration because it lets an AI client discover and call `run_managed_agent` as a tool. The OpenAPI adapter is the fallback for clients that can call REST endpoints but do not support MCP.

## 1. MCP server

Install dependencies:

```bash
pip install -U google-genai mcp
export GEMINI_API_KEY="your-key"
python integrations/managed_agent_mcp_server.py
```

The server exposes:

- `run_managed_agent`: execute a prompt with a managed agent.
- `continue_managed_agent`: continue an existing sandbox/conversation using its IDs.

### Gemini CLI configuration

Add this server to the Gemini CLI MCP configuration (the exact configuration location can vary by CLI release):

```json
{
  "mcpServers": {
    "managed-agents": {
      "command": "python",
      "args": ["/absolute/path/to/manus-agente/integrations/managed_agent_mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

The same MCP process can be registered with any MCP-compatible client, including Manus integrations that support MCP.

## 2. OpenAPI/HTTP adapter

Install dependencies and start it:

```bash
pip install -U google-genai fastapi uvicorn
export GEMINI_API_KEY="your-key"
uvicorn integrations.openapi_server:app --host 127.0.0.1 --port 8080
```

Import `integrations/managed-agent.openapi.yaml` into a client that supports OpenAPI actions, or call it directly:

```bash
curl -X POST http://127.0.0.1:8080/v1/managed-agent/run \
  -H 'content-type: application/json' \
  -d '{"input":"Analyze this request and answer concisely.","agent":"antigravity-preview-05-2026"}'
```

For a hosted deployment, put the endpoint behind HTTPS and add authentication before exposing it publicly. Never put `GEMINI_API_KEY` in a client prompt, notebook output, OpenAPI document, or browser code.

## Conversation state

The response includes `interaction_id` and `environment_id`. Pass them back on the next call to preserve context:

```json
{
  "input": "Now summarize the result in three bullets.",
  "environment_id": "...",
  "previous_interaction_id": "..."
}
```

An environment ID preserves the remote sandbox. A previous interaction ID preserves the interaction chain. Persist both in the calling application if multi-turn workflows are required.

## Security and production notes

- Keep the server on `127.0.0.1` for local clients; use HTTPS, authentication, rate limits, and audit logs for remote clients.
- Treat prompts and files supplied to the managed agent as untrusted input.
- Do not return internal step traces by default; the adapters return only the final text and IDs.
- Set request timeouts and quotas in the hosting layer.
- The managed agent and its remote environment may incur latency or usage charges.
- The API and preview agent name can change; configure `MANAGED_AGENT` rather than hard-coding it in deployments.
