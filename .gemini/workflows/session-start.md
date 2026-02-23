# Workflow: Session Start

## Purpose
Initialize a development session with full project context.

## Steps

### 1. Load Context
```
- Read docs/DEVLOG.md (last entry)
- Read docs/TODO.md (pending tasks)
- Read CHANGELOG.md (latest version)
```

### 2. Check Git Status
```bash
git log --oneline -10
git status
```

### 3. Generate Summary
Present:
- Last work completed
- Priority pending tasks
- Uncommitted changes
- Suggested next action

## Invocation
```bash
gemini /session:start
```

## Expected Output
```
═══════════════════════════════════════
📋 SESSION STARTED
═══════════════════════════════════════
📅 Date: YYYY-MM-DD

📝 Last Session:
   - [summary of last DEVLOG entry]

📌 Priority Tasks:
   1. [task 1]
   2. [task 2]

📂 Git Status:
   - [uncommitted changes summary]

💡 Suggested Next Step:
   - [recommendation]
═══════════════════════════════════════
```
