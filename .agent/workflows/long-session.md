---
description: How to manage long development sessions with context compaction (Opus 4.6)
---

# Long Session Management Workflow

This workflow ensures context quality during extended development sessions by leveraging Claude Opus 4.6's compaction API.

## When to Use
- Sessions exceeding 30 minutes of active work
- Working across 10+ files in a single session
- When you notice degraded response quality (a sign of context pressure)

## Steps

1. **Monitor context pressure**
   - Claude Code auto-compacts at ~75% of context window
   - Watch for the compaction indicator in the CLI output
   - If you notice slower responses, proactively compact

2. **Proactive compaction** (recommended)
   ```
   /compact Preserve: architecture decisions, file paths, current task state, and error context
   ```

3. **Before compaction, save state**
   - Ensure current progress is documented in `docs/DEVLOG.md`
   - Any in-progress decisions should be in `docs/decisions/`
   - Critical context should be in `CLAUDE.md` (survives compaction)

4. **After compaction, re-anchor**
   - Claude will re-read `CLAUDE.md` automatically
   - Briefly summarize the current task to re-establish context
   - Reference specific files rather than expecting recall of file contents

5. **Session end protocol**
   - Run `/compact` one final time with focus on session outcomes
   - Update `docs/DEVLOG.md` with session accomplishments
   - Commit any pending changes

## Tips
- Put persistent rules in `CLAUDE.md` — they survive all compactions
- Use `/compact` with a specific focus rather than letting auto-compaction decide
- For very long sessions (2h+), consider starting a fresh session instead
- The `/debug` command can help inspect current session state if something feels off
