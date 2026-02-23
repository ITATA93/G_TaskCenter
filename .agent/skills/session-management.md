# Skill: Session Management

> **Universal** — Works across all vendors (Gemini, Claude, Codex)

## Purpose

Manage session continuity by auto-loading context and persisting session results.

## Session Start

When an agent starts a session on this project:

1. **Read** `docs/TODO.md` — identify blockers and in-progress tasks
2. **Read** the latest entry in `docs/DEVLOG.md` — last session context
3. **Present summary** to user before acting:
   > "Last session: [topic]. Pending: [N tasks]. Continue with [in-progress]?"
4. **Wait** for user direction

## Session End

Before closing:

1. Update `docs/TODO.md` — mark completed, add discovered tasks
2. Append structured entry to `docs/DEVLOG.md`
3. Run: `python scripts/knowledge_sync.py`

## Manual Sync

```bash
python scripts/knowledge_sync.py              # Full sync
python scripts/knowledge_sync.py --snapshot    # Context snapshot only
python scripts/knowledge_sync.py --index       # Update memory index only
```

## Key Files

| File                                | Purpose                                        |
| ----------------------------------- | ---------------------------------------------- |
| `docs/TODO.md`                      | Task tracker (Blocker/InProgress/Backlog/Done) |
| `docs/DEVLOG.md`                    | Session diary (structured entries)             |
| `.gemini/brain/context-snapshot.md` | Auto-generated context (<50 lines)             |
| `.gemini/brain/memory-index.md`     | Persistent knowledge index                     |
