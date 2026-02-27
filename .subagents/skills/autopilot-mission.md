---
description: "Parse and execute a mission brief in Autopilot mode"
trigger: "/autopilot <mission>"
vendors: [claude, gemini, codex]
depends_on:
  - .agent/workflows/autopilot.md
  - .agent/rules/autopilot-guardrails.md
  - .agent/workflows/turbo-ops.md
---

# Skill: Autopilot Mission

Execute a complete development mission autonomously — zero user intervention
after the initial mission brief.

## Invocation

```
/autopilot <goal description>
```

Optional inline constraints (parsed from natural language):
```
/autopilot <goal>. Max N files, allow new files, auto-push.
```

## Execution Flow

### Phase 1: Parse Mission (instant)

Extract from user input:
- **goal**: The objective (required)
- **constraints**: Any mentioned limits (optional, defaults apply)
- **scope hints**: File paths, service names, or patterns mentioned

Normalize into the mission YAML structure defined in `autopilot.md`.
Print the parsed mission to the user:

```
AUTOPILOT ENGAGED
Mission: <goal>
Branch: autopilot/<slug>
Constraints: <summary>
Kill switches: ACTIVE
```

### Phase 2: Pre-Flight (auto)

1. Read `docs/TODO.md` and `docs/DEVLOG.md` (last entry) for context
2. Stash uncommitted changes if any
3. Create and checkout `autopilot/<slug>` branch
4. Explore codebase to identify affected files
5. Generate internal execution plan
6. Validate plan against constraints

If pre-flight fails, print reason and return control to user.

### Phase 3: Execute (auto)

Run the execution plan following autopilot guardrails:

- Make code changes within scope
- Use decision engine for ambiguities (prefer reversible, minimal, conventional)
- Log each decision internally
- Run tests after each logical unit
- Auto-commit with conventional messages
- Create checkpoints every 5 operations
- Monitor constraints continuously

If any kill switch triggers → Phase 5 (abort path).
If any constraint is exceeded → Phase 5 (partial completion).

### Phase 4: Post-Flight (auto)

1. Run full test suite
2. Generate post-flight report
3. Print report to user
4. Append abbreviated entry to `docs/DEVLOG.md`
5. Stay on autopilot branch (user decides merge strategy)

### Phase 5: Abort (if needed)

1. Stop current operation
2. Commit WIP on autopilot branch
3. Generate post-flight with ABORTED status
4. Print report with explanation
5. Suggest recovery options to user

## Natural Language Constraint Parsing

The skill parses common phrases into constraint overrides:

| User says | Constraint set |
|---|---|
| "max N files" | `max_files_changed: N` |
| "no new files" | `allow_new_files: false` |
| "can delete files" | `allow_delete_files: true` |
| "allow dependencies" | `allow_dependency_changes: true` |
| "auto-push" / "push when done" | `auto_push: true` |
| "keep it small" | `max_files_changed: 5, max_lines_delta: 100` |
| "go wild" / "sin limites" | `max_files_changed: 50, max_lines_delta: 2000` |

## Decision Engine Heuristics

When facing a choice with no explicit user guidance:

```
Priority 1: Does existing code already have a pattern? → Follow it
Priority 2: Is one option more reversible? → Choose it
Priority 3: Is one option simpler? → Choose it
Priority 4: Is one option more secure? → Choose it
Priority 5: Default to the most conservative option
```

Every decision is logged with:
- Decision point (what was the question)
- Options considered
- Option chosen
- Reasoning

## Error Recovery

```
Error occurs
  ├── Known pattern? → Apply known fix
  ├── Test failure? → Read error, attempt fix (max 2x)
  ├── Import error? → Check if dependency is allowed, install if yes
  ├── Syntax error? → Self-correct from error message
  ├── Same error 3x? → ABORT (error loop)
  └── Unknown? → Log, skip operation, continue with next step
```

## Vendor-Specific Behavior

### Claude (Opus 4.6)
- Full parallel execution via Task tool
- Internal agents available for code review sub-tasks
- Extended thinking for complex decisions

### Gemini
- Sequential subagent execution
- Use code execution sandbox for validation
- Brain memory system for cross-checkpoint state

### Codex
- Sequential execution only (no Task tool)
- Use effort levels: `xhigh` for planning, `high` for execution
- Extended reasoning for decision engine

## Examples

### Basic
```
/autopilot Add error handling to all FastAPI endpoints in services/mcp_server/
```
→ Scope: `services/mcp_server/src/**/*.py`
→ Constraints: defaults
→ Branch: `autopilot/add-error-handling-fastapi`

### Constrained
```
/autopilot Refactor Docker setup to multi-stage builds. Max 5 files, no deps.
```
→ Scope: `Dockerfile`, `docker-compose.yml`, `docker/**`
→ Constraints: max_files=5, allow_dependency_changes=false
→ Branch: `autopilot/refactor-docker-multistage`

### Infrastructure
```
/autopilot Create monitoring script for all 22 services. Register in library.
```
→ Scope: `scripts/`, `docs/library/scripts.md`
→ Constraints: defaults, allow_new_files=true
→ Branch: `autopilot/create-monitoring-script`
