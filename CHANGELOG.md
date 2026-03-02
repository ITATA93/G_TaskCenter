---
depends_on: []
impacts: [CHANGELOG.md]
---

# CHANGELOG - G_TaskCenter

## [Unreleased]

### Added

- CLI authentication module for Gmail OAuth2 and Microsoft Graph device-code flow (`src/auth/cli_auth.py`).
- Task deduplication and unification engine with fuzzy matching (`src/dedup/unifier.py`).
- Slack integration: read task-flagged messages, mark done via reaction (`src/integrations/slack.py`).
- Jira integration: list assigned issues, transition issues via workflow (`src/integrations/jira.py`).
- SQLite persistence layer with tasks, sources, and sync_log tables (`src/db/sqlite_store.py`).
- Automated test suite: `tests/test_auth.py`, `tests/test_unifier.py`, `tests/test_sqlite_store.py`.
- GEN_OS pre-classifier routing configuration for task-related queries (`config/routing.json`).
- MCP implementation decision record (`docs/MCP_DECISION.md`): FastMCP via `src/server.py` is canonical.
- Integration documentation for all 6 sources (`docs/INTEGRATIONS.md`).

### Changed

- Enhanced README.md with structured sections: Proposito, Arquitectura, Uso con Gemini CLI, Scripts, Configuracion.
- Updated `docs/TODO.md` and `docs/TASKS.md`: all 9 pending items marked complete.

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
