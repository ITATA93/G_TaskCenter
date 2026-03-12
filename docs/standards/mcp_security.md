---
title: MCP Security Middleware Standard
depends_on:
  - infrastructure/mcp-servers/shared/middleware.py
  - infrastructure/mcp-servers/shared/db.py
  - infrastructure/migrations/002_audit_triggers.sql
  - docs/standards/quality_gates.md
impacts:
  - docs/standards/quality_gates.md
---

# MCP Security Middleware Standard

Version: 1.0.0
Reference date: 2026-02-22

## 1. Purpose

This standard defines the security middleware layer applied to all MCP (Model Context Protocol) server tool functions in GEN_OS. The middleware enforces authorization, audit trail, and rate limiting at the tool invocation level.

## 2. Architecture

All 4 MCP servers (memory, tasks, prompts, workflows) use the `@secured_tool()` decorator from `infrastructure/mcp-servers/shared/middleware.py`. The decorator wraps each `@mcp.tool()` function and enforces:

1. **Authorization**: Agent's `risk_tier` must meet or exceed the tool's `min_risk` requirement.
2. **Rate Limiting**: Per-agent call frequency limited by sliding window (configurable via `MCP_RATE_LIMIT_PER_MINUTE` env var, 0 = disabled).
3. **Audit Trail**: Every tool invocation (success, denial, rate limit) is logged to the `audit_log` table.

## 3. Tool Authorization Matrix

| Server | Tool | min_risk | operation |
|--------|------|----------|-----------|
| memory | `add_memory` | low | write |
| memory | `search_memory` | low | read |
| memory | `list_memories` | low | read |
| memory | `delete_memory` | medium | delete |
| tasks | `create_task` | low | write |
| tasks | `update_task` | low | write |
| tasks | `list_tasks` | low | read |
| tasks | `get_project_tasks` | low | read |
| prompts | `create_prompt` | medium | write |
| prompts | `update_prompt_label` | medium | write |
| prompts | `get_prompt` | low | read |
| prompts | `list_prompts` | low | read |
| workflows | `create_workflow` | high | write |
| workflows | `update_workflow_status` | high | write |
| workflows | `get_workflow` | low | read |
| workflows | `list_workflows` | low | read |

## 4. Risk Tier Ordering

```
low (0) < medium (1) < high (2) < critical (3)
```

An agent with `risk_tier: "medium"` can access tools requiring `min_risk: "low"` or `"medium"`, but not `"high"` or `"critical"`.

## 5. RequestContext

Each tool invocation carries a `RequestContext` dataclass:

- `agent_id`: Identifier of the calling agent (default: "anonymous")
- `risk_tier`: Agent's declared risk tier (default: "low")
- `intent_id`: Correlation ID for intent tracking
- `trace_id`: Unique trace ID for observability (auto-generated if not provided)
- `timestamp`: UTC timestamp of the invocation

Context is passed via reserved kwargs: `_agent_id`, `_risk_tier`, `_intent_id`, `_trace_id`.

## 6. Audit Trail Schema

The middleware writes to the existing `audit_log` table with extended ACTION types:

| ACTION | Description |
|--------|-------------|
| `CALL` | Successful tool invocation |
| `DENIED` | Authorization failure (insufficient risk tier) |
| `RATE_LIMITED` | Rate limit exceeded |
| `INSERT` | DB-level trigger (row inserted) |
| `UPDATE` | DB-level trigger (row updated) |
| `DELETE` | DB-level trigger (row deleted) |

Migration `002_audit_triggers.sql` extends the CHECK constraint and adds DB-level triggers for defense-in-depth.

## 7. Rate Limiting Policy

- Default: Disabled (`MCP_RATE_LIMIT_PER_MINUTE=0`)
- Recommended production value: 60 calls/minute/agent
- Implementation: In-memory sliding window with `asyncio.Lock`
- Known limitation: State lost on server restart (acceptable for stdio transport)

## 8. Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MCP_RATE_LIMIT_PER_MINUTE` | `0` | Max calls per agent per minute (0 = disabled) |
| `MCP_AUDIT_ENABLED` | `true` | Enable/disable audit trail writes |

## 9. Deployment

To apply middleware to a new MCP tool:

```python
from shared.middleware import secured_tool

@mcp.tool()
@secured_tool(min_risk="low", operation="read")
async def my_new_tool(...) -> str:
    ...
```

The `@secured_tool` decorator must always be the inner decorator (after `@mcp.tool()`).
