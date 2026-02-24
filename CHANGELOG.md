---
depends_on: []
impacts: [CHANGELOG.md]
---

# CHANGELOG - G_TaskCenter

## [Unreleased]

### Changed
- Enhanced README.md with structured sections: Proposito, Arquitectura, Uso con Gemini CLI, Scripts, Configuracion.

## [0.1.0] - 2026-02-23

### Added

- Official MCP local server implementation in `src/server.py` with `list_unified_tasks` tool.
- MCP server implementation in `scripts/mcp_server.py` using FastMCP.
- Gmail integration in `src/integrations/gmail.py`.
- Notion integration in `src/integrations/notion.py`.
- Outlook integration in `src/integrations/outlook.py`.
- `requirements.txt` with necessary dependencies.
- `.env.example` for credential configuration.
- `docs/setup_mcp.md` documentation for server setup and tool usage.
