---
description: "Fully autonomous execution mode — zero user intervention after mission brief"
tier: autopilot
extends: turbo-ops
---

// autopilot

# Autopilot Mode

> **Tier**: Beyond Turbo. User provides a **Mission Brief** once; the agent plans,
> executes, commits, and reports — all without further intervention.

## Activation

The user triggers Autopilot with the `/autopilot` command or by saying
"autopilot", "modo autonomo", "zero-touch", or "sin intervencion".

When activated, the agent MUST:
1. Parse the mission brief
2. Create a git safety branch
3. Execute the full pipeline
4. Generate a post-flight report
5. Return control to user

---

## 1. Mission Brief Format

The user provides a goal. The agent normalizes it into:

```yaml
mission:
  goal: "<one-line objective>"
  scope:
    files: ["<glob patterns or specific files>"]    # auto-detected if omitted
    services: ["<affected services>"]               # auto-detected if omitted
  constraints:
    max_files_changed: 20                            # default: 20
    max_lines_delta: 500                             # default: 500
    allow_new_files: true                            # default: true
    allow_delete_files: false                        # default: false
    allow_dependency_changes: false                  # default: false
    auto_commit: true                                # default: true
    auto_push: false                                 # default: false (never to main)
    target_branch: "autopilot/<slug>"                # auto-generated
  kill_switch:                                       # NEVER overridable
    - database_destructive_ops
    - force_flags
    - main_branch_push
    - secrets_exposure
    - ops_outside_workspace
    - git_reset_hard
    - uninstall_packages
```

If the user omits constraints, defaults apply. The agent MUST NOT ask for
clarification on missing optional fields — use safe defaults and proceed.

---

## 2. Pre-Flight (Automatic)

Before any code changes, the agent executes these steps autonomously:

```
PRE-FLIGHT CHECKLIST
[x] 1. Parse mission brief → normalize to YAML structure
[x] 2. Read docs/TODO.md + docs/DEVLOG.md (last entry) → context
[x] 3. git stash (if dirty working tree) → preserve user work
[x] 4. git checkout -b autopilot/<slug> → safety branch
[x] 5. Explore codebase → identify affected files
[x] 6. Generate execution plan (internal, not shown to user)
[x] 7. Validate plan against constraints + kill switches
[x] 8. Begin execution
```

**Critical**: Step 3 ensures user's uncommitted work is never lost.
**Critical**: Step 4 ensures all changes happen on an isolated branch.

---

## 3. Execution Engine

### 3.1 Auto-Approved Operations (extends Turbo)

Everything in `turbo-ops.md` PLUS:

| Operation | Condition |
|---|---|
| `git commit` | Conventional commit message, on autopilot/* branch only |
| `git push -u origin autopilot/*` | Only autopilot branches, never main/master |
| File creation | Within project, respects `safe-write` zones |
| File editing | Within scope.files constraint |
| File deletion | Only if `allow_delete_files: true` |
| `pip install` / `npm install` | Only if `allow_dependency_changes: true` |
| Run tests | Always auto-approved |
| Run linters | Always auto-approved |

### 3.2 Decision Engine

When the agent hits an ambiguity or choice point, instead of asking the user:

1. **Prefer reversible** — choose the option that is easiest to undo
2. **Prefer minimal** — choose the smallest change that satisfies the goal
3. **Prefer conventional** — follow existing project patterns and conventions
4. **Log the decision** — record in internal decision log for post-flight report

```
DECISION LOG ENTRY:
  point: "Whether to use async or sync HTTP client"
  options: ["httpx.AsyncClient", "requests.Session"]
  chosen: "httpx.AsyncClient"
  reason: "Existing codebase uses async patterns (found in services/mcp_server/)"
```

### 3.3 Checkpoint System

Every 5 significant operations, the agent creates an internal checkpoint:

```
CHECKPOINT #N
  operations_completed: 12
  files_changed: ["path/a.py", "path/b.ts"]
  tests_passing: true/false
  constraints_status: within_limits
  next_action: "Implement validation logic in schema.py"
```

If tests fail at a checkpoint:
1. Attempt auto-fix (max 2 retries)
2. If still failing → stop, commit WIP, generate post-flight with failure status

### 3.4 Constraint Enforcement

The agent continuously monitors against mission constraints:

- **max_files_changed**: If approaching limit, prioritize remaining changes
- **max_lines_delta**: If approaching limit, stop adding non-essential changes
- **scope.files**: Never touch files outside declared scope
- **kill_switch**: Immediately abort operation, commit WIP, report breach

---

## 4. Kill Switch Boundaries

These are **ABSOLUTE** and **NEVER OVERRIDABLE**, even if the mission brief
explicitly requests them:

| Boundary | What It Blocks |
|---|---|
| `database_destructive_ops` | INSERT/UPDATE/DELETE/DROP/TRUNCATE on any database |
| `force_flags` | Any `--force`, `-f` on destructive commands |
| `main_branch_push` | `git push` to main, master, or production branches |
| `secrets_exposure` | Writing API keys, tokens, passwords to tracked files |
| `ops_outside_workspace` | File operations outside the project directory |
| `git_reset_hard` | `git reset --hard`, `git checkout .`, `git clean -f` |
| `uninstall_packages` | `pip uninstall`, `npm uninstall`, `apt remove` |

If a kill switch triggers:
1. **STOP** the current operation immediately
2. **DO NOT** attempt the blocked action
3. **Commit** work done so far as WIP
4. **Report** the kill switch breach in post-flight
5. **Return** control to user with explanation

---

## 5. Commit Strategy

On the autopilot branch, the agent commits automatically:

### Commit Frequency
- After each logical unit of work (1 feature, 1 fix, 1 refactor)
- At each checkpoint if tests pass
- Before any risky operation (safety snapshot)
- On completion or abort

### Commit Message Format
```
autopilot(<scope>): <conventional description>

Mission: <mission.goal>
Checkpoint: #N
Files: <count> changed

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Branch Strategy
```
main ──────────────────────────────────────
        \
         autopilot/add-validation-layer ── commits ── final
```

The user decides whether to merge, squash, or discard the branch.

---

## 6. Post-Flight Report

When the mission completes (or aborts), the agent generates:

```markdown
## Autopilot Post-Flight Report

### Mission
- **Goal**: <mission.goal>
- **Status**: COMPLETED | PARTIAL | ABORTED
- **Branch**: autopilot/<slug>
- **Duration**: <N operations, M commits>

### Changes Summary
| File | Action | Lines |
|---|---|---|
| path/to/file.py | modified | +15 / -3 |
| path/to/new.py | created | +42 |

### Decision Log
1. <decision point> → <chosen option> (reason)
2. ...

### Test Results
- Tests run: N
- Passed: N
- Failed: N (if any, with details)

### Constraints Status
- Files changed: X / max_files_changed
- Lines delta: +X/-Y / max_lines_delta
- Kill switches triggered: none | [list]

### Next Steps (for user)
- [ ] Review changes: `git diff main...autopilot/<slug>`
- [ ] Merge if satisfied: `git merge autopilot/<slug>`
- [ ] Or discard: `git branch -D autopilot/<slug>`
```

This report is:
1. Printed to the user in the conversation
2. Appended to `docs/DEVLOG.md` (abbreviated form)
3. Not saved as a separate file (follows output governance)

---

## 7. Abort Conditions

The agent auto-aborts (stops, commits WIP, reports) if:

1. **Kill switch triggered** — hard stop
2. **Tests fail after 2 retries** — can't auto-fix
3. **Constraint limit reached** — max files or lines exceeded
4. **Error loop detected** — same error 3 times in a row
5. **Scope creep detected** — changes needed outside declared scope
6. **Context pressure** — at 75% context window, compact and continue;
   at 90%, commit WIP and stop

The agent NEVER aborts silently — always commits WIP and generates a report.

---

## 8. Comparison: Modes

| Feature | Normal | Turbo | Autopilot |
|---|---|---|---|
| Read ops | ask | auto | auto |
| Safe writes | ask | auto | auto |
| File edits | ask | ask | auto (within scope) |
| git commit | ask | ask | auto (autopilot/* branch) |
| git push | ask | ask | auto (autopilot/* only) |
| Decisions | ask user | ask user | decision engine |
| Tests | ask | auto | auto + auto-fix |
| Destructive ops | ask | ask | **BLOCKED** (kill switch) |
| Report | none | none | post-flight report |
| Rollback | manual | manual | git branch delete |

---

## 9. Usage Examples

### Simple
```
/autopilot Add input validation to all API endpoints in services/mcp_server/
```

### With constraints
```
/autopilot Refactor the Docker setup to use multi-stage builds.
Constraints: max 5 files, no dependency changes, auto-push to remote.
```

### Infrastructure
```
/autopilot Create a health-check script that pings all 22 services
and reports status. Register it in docs/library/scripts.md.
```
