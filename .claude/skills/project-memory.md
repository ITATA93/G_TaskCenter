# Skill: Project Memory

## Purpose
Maintain persistent project memory through structured documentation.
Auto-activates at session start and end.

## Behavior

### On Session Start
1. Read docs/DEVLOG.md for previous work context
2. Read docs/TODO.md for current priorities
3. Read docs/architecture/*.md for active decisions

### On Task Completion
1. Update docs/DEVLOG.md with completed work
2. Update CHANGELOG.md if feature/fix completed
3. Update docs/TODO.md (mark done, add discovered tasks)

### On Significant Changes
- New queries → docs/database/
- New endpoints → docs/api/
- Architecture changes → docs/architecture/
- Decisions → docs/decisions/

## Key Files

| File | Update When |
|------|-------------|
| DEVLOG.md | After any task completion |
| CHANGELOG.md | After features or fixes |
| TODO.md | After completing or discovering tasks |
| docs/api/*.md | After API changes |
| docs/architecture/*.md | After design decisions |

## Memory Structure
```
docs/
├── DEVLOG.md          ← Session diary
├── TODO.md            ← Task tracking
├── research/          ← Deep research results
├── architecture/      ← Design docs
├── api/               ← API documentation
├── database/          ← DB schemas and queries
└── decisions/         ← ADRs
```

## Invocation
This skill runs automatically. Can be manually triggered:
```bash
gemini /memory:sync
```
