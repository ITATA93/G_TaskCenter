---
depends_on:
  - docs/library/INDEX.md
impacts:
  - CLAUDE.md
  - GEMINI.md
  - .agent/rules/session-protocol.md
  - docs/plans/gen_os_master_bootstrap_plan_v1.md
---

# Output Governance Standard - GEN_OS

Version: 1.1.0  
Scope: `GEN_OS` core and `G_<Nombre>` satellites.

This standard defines where and how agents can create files in this ecosystem.

## 1. Core Principle

Project root is immutable for ad-hoc agent outputs.

Only standardized root-level files are allowed (for example: `.env`, `.gitignore`, `README.md`, `CHANGELOG.md`, `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`).

## 2. Approved Output Directories

### Documentation and Records
- Implementation plans: `docs/plans/[plan_name].md`
- Architecture decisions (ADRs): `docs/decisions/ADR-[number]_[short_title].md`
- Audits: `docs/audit/`
- Research: `docs/research/`
- Workflow system: `docs/workflows/`
  - Specs: `docs/workflows/spec/*.yaml`
  - Visual diagrams: `docs/workflows/design/*.md`
  - Generated registry: `docs/workflows/registry/workflow_registry.json`

### Capability Inventory (Living Dictionary)

Every automated artifact (agent, command, script, workflow, prompt, plugin) must be registered in:

- `docs/library/INDEX.md`
- `docs/library/commands.md`
- `docs/library/agents.md`
- `docs/library/workflows.md`
- `docs/library/scripts.md`
- `docs/library/mcp_plugins.md`
- `docs/library/prompts.md`

### Temporary Scripts

One-off utilities should be placed in `scripts/temp/` (gitignored).

## 3. Naming Conventions

- Markdown files (except standard root docs) should use `snake_case` or ADR format.
- Avoid spaces and special characters in paths.

## 4. Text Style Rule (No Emojis)

- Emojis are not allowed in documentation, commands, prompts, reports, or persisted repository text.
- Use neutral textual labels: `PASS`, `FAIL`, `PARTIAL`, `HIGH`, `MEDIUM`, `LOW`.
- Applies to:
  - `docs/**/*.md`
  - `.claude/commands/*`
  - `.gemini/commands/*`
  - root markdown files

## 5. Change Control

Changes to this standard require validation against the corresponding ADR and security review.
