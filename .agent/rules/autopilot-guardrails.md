---
description: "Automatic safety guardrails for Autopilot mode — replaces interactive confirmations"
applies_to: autopilot
impacts:
  - .agent/workflows/autopilot.md
  - .agent/workflows/turbo-ops.md
  - .subagents/safe-write.sh
---

# Autopilot Guardrails

> These rules are **automatically enforced** during Autopilot mode.
> They replace interactive user confirmations with programmatic checks.

## 1. Branch Isolation (MANDATORY)

All Autopilot work MUST happen on a dedicated branch:

```
Branch naming: autopilot/<kebab-case-slug>
```

**Rules:**
- NEVER commit directly to `main`, `master`, or `production`
- NEVER merge autopilot branches automatically
- ALWAYS create the branch BEFORE any file modifications
- If the branch already exists, append a counter: `autopilot/<slug>-2`

**Verification** (before each commit):
```bash
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
  ABORT "Kill switch: attempting to commit on protected branch"
fi
```

## 2. Stash Protection

Before switching branches, protect user's work:

```bash
# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  git stash push -m "autopilot-safeguard-$(date +%s)"
fi
```

**On Autopilot completion**, remind the user:
```
Note: Your uncommitted work was stashed. Run `git stash pop` to restore.
```

## 3. Scope Enforcement

### File Scope
- Only modify files matching `mission.scope.files` patterns
- If scope is auto-detected, limit to files directly related to the goal
- NEVER modify governance files (CLAUDE.md, GEMINI.md, AGENTS.md) in Autopilot
- NEVER modify `.env` files or any file matching `*.secret*`, `*.key`, `*.pem`

### Change Limits
Monitor continuously:
```
files_changed <= mission.constraints.max_files_changed  (default: 20)
lines_added + lines_removed <= mission.constraints.max_lines_delta  (default: 500)
```

If a limit is reached:
1. Commit current work with message `autopilot: WIP — constraint limit reached`
2. Stop execution
3. Report in post-flight

## 4. Commit Guardrails

### Auto-Commit Rules
Commits happen automatically ONLY when ALL conditions are met:
- [x] On an `autopilot/*` branch
- [x] Changes are within declared scope
- [x] No kill switch has been triggered
- [x] Commit message follows conventional format

### Commit Message Validation
Every auto-commit message MUST:
- Start with `autopilot(<scope>):` prefix
- Be under 72 characters for the first line
- Include the mission goal in the body
- Include the `Co-Authored-By` trailer

### Forbidden in Commits
NEVER commit files matching:
- `.env`, `.env.*` (except `.env.example`)
- `*.secret`, `*.key`, `*.pem`, `*.p12`
- `credentials.*`, `token.*`
- `node_modules/`, `__pycache__/`, `.venv/`

## 5. Execution Guardrails

### Error Loop Detection
Track consecutive errors per operation type:
```
error_count[operation] += 1
if error_count[operation] >= 3:
  ABORT "Error loop detected: {operation} failed 3 times"
```

Reset counter on success.

### Timeout per Operation
- Read operations: 30 seconds
- Write operations: 60 seconds
- Test execution: 300 seconds (5 min)
- Build operations: 600 seconds (10 min)

If timeout is reached, skip operation and log it.

### Dependency Lock
When `allow_dependency_changes: false` (default):
- BLOCK `pip install`, `npm install`, `apt install`
- BLOCK any modification to `requirements.txt`, `package.json`, `Pipfile`
- BLOCK Dockerfile changes that add new dependencies

When `allow_dependency_changes: true`:
- ALLOW additive installs only
- BLOCK `uninstall`, `remove`, `purge` (kill switch)

## 6. Test Guardrails

### Auto-Test Policy
After each logical change unit:
1. Run existing tests related to modified files
2. If tests fail → attempt auto-fix (max 2 attempts)
3. If still failing → commit WIP, stop, report

### Test Discovery
```
Modified: src/foo/bar.py  →  Look for: tests/test_bar.py, tests/foo/test_bar.py
Modified: services/x.py   →  Look for: tests/test_x.py, tests/services/test_x.py
```

If no tests exist for modified files, note it in the post-flight report
but do NOT auto-generate tests (that's scope creep unless explicitly requested).

## 7. Context Management

### Compaction Strategy
- At 75% context: `/compact` preserving mission state + decision log
- At 90% context: commit WIP, generate partial report, STOP
- ALWAYS save mission state to internal checkpoint before compaction

### State Preservation
The following MUST survive compaction:
- Mission brief (goal + constraints)
- Current execution step
- Decision log
- Files changed so far
- Test status

## 8. Output Governance (Autopilot-Specific)

Autopilot follows all standard output governance rules PLUS:
- Post-flight report goes to conversation output + DEVLOG.md (abbreviated)
- NO separate report files are created
- Decision log is ephemeral (only in post-flight, not persisted separately)
- Checkpoints are internal only, not written to files

## 9. Abort Protocol

When aborting, ALWAYS execute in this order:

```
1. STOP current operation (do not complete it)
2. git add -A && git commit -m "autopilot: WIP — aborted (<reason>)"
3. Generate post-flight report with status: ABORTED
4. Print report to user
5. Append abbreviated entry to docs/DEVLOG.md
6. DO NOT switch branches (leave user on autopilot/* for inspection)
7. Inform user: "Branch autopilot/<slug> contains partial work.
   Review with: git diff main...autopilot/<slug>"
```

## 10. What Autopilot CANNOT Do

Even in full autonomy, these actions are **permanently blocked**:

| Action | Reason |
|---|---|
| Modify CLAUDE.md / GEMINI.md | Governance files are human-maintained |
| Push to main/master | Protected branches |
| Delete branches | User decides branch lifecycle |
| Run database migrations | Data integrity risk |
| Modify CI/CD configs | Blast radius too large |
| Access external APIs with write ops | Side effects outside workspace |
| Create cron jobs or scheduled tasks | Persistent side effects |
| Modify system-level configs | Outside project scope |
