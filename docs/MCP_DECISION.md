# MCP Implementation Decision Record

**Status:** Accepted
**Date:** 2026-03-01
**Decision:** Use **FastMCP** as the canonical MCP implementation for G_TaskCenter.

## Context

G_TaskCenter had two MCP server implementations:

1. **`src/server.py`** — Full-featured server using `fastmcp.FastMCP` with 10 tools
   (read, write, and n8n workflow automation). Uses Pydantic model serialization.
2. **`scripts/mcp_server.py`** — Legacy/alternative server using `mcp.server.fastmcp.FastMCP`
   with 4 read-only tools. Retained for backward compatibility.

Both implementations use FastMCP under the hood (the `mcp` package re-exports it).
A decision was needed to designate one as canonical.

## Decision

**`src/server.py` is the canonical MCP server**, using the `fastmcp` package directly.

### Rationale

| Criterion                | `src/server.py`      | `scripts/mcp_server.py`     |
|--------------------------|----------------------|-----------------------------|
| Tool count               | 10 (full surface)    | 4 (read-only subset)        |
| Write operations         | Yes                  | No                          |
| n8n integration          | Yes                  | No                          |
| Pydantic serialization   | Yes                  | Manual JSON dumps           |
| Async support            | Sync (FastMCP)       | Async tools                 |
| Registration target      | `G_TaskCenter`       | `g-taskcenter`              |
| Maintenance burden       | Primary, active      | Legacy, passive             |

### Key factors

1. **Feature completeness**: `src/server.py` exposes the full tool surface including
   task creation, completion, and n8n workflow automation.
2. **Type safety**: Uses Pydantic `model_dump()` for consistent serialization.
3. **Single source of truth**: Avoids drift between two implementations.
4. **FastMCP maturity**: The `fastmcp` package is stable and well-maintained,
   providing stdio transport, tool registration, and lifecycle management.

## Consequences

- **`scripts/mcp_server.py`** is marked as LEGACY in its docstring and will NOT
  receive new tools. It remains available for lightweight read-only usage.
- All new MCP tools MUST be added to `src/server.py`.
- The GEN_OS routing configuration (`config/routing.json`) references `src/server.py`
  as the entry point.
- MCP client registration (e.g., in Claude Desktop `mcpServers` config) should point to:
  ```json
  {
    "g-taskcenter": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "<path-to-G_TaskCenter>"
    }
  }
  ```

## Alternatives Considered

1. **Migrate to the raw `mcp` SDK**: More control but significantly more boilerplate.
   FastMCP is the recommended high-level wrapper.
2. **Merge both servers**: Would break backward compatibility for existing consumers
   of the legacy endpoint.
3. **Use a different framework (e.g., custom HTTP)**: MCP is the ecosystem standard
   for tool exposure in the Antigravity OS workspace.
