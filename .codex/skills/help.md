---
name: Help Command
description: Provide user guide and assistance for Antigravity Workspace.
---

# Help Skill

When the user asks for help, support, or how to use the system (e.g., "/help", "@Ayuda"):

1.  **Read `docs/GUIDE.md`** only if you haven't read it in this session.
2.  Summarize the key points for the user:
    *   **Quick Start**: How to start/end sessions.
    *   **Agents**: List available agents (code-analyst, doc-writer, etc.) and what triggers them.
    *   **Migration**: Steps to migrate existing projects.
3.  Offer to perform specific actions like `gemini /session:start` or running an analysis.

**Context**: You are operating in a multi-model environment. Refer to `.subagents/manifest.json` if the user asks about specific agents configuration.
