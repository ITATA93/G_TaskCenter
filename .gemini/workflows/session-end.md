# Workflow: Session End

## Purpose
Close development session properly with documentation and optional commit.

## Steps

### 1. Review Changes
```bash
git diff --stat
git status
```

### 2. Update Documentation
- Add entry to docs/DEVLOG.md:
  - Date (ISO 8601)
  - What was done
  - Decisions made
  - Next steps
- Update CHANGELOG.md if features/fixes completed
- Update docs/TODO.md (mark completed, add new)

### 3. Run Tests (if applicable)
```bash
# Python
pytest tests/ -v --tb=short

# JavaScript/TypeScript
npm test
```

### 4. Commit (if tests pass)
```bash
git add -A
git commit -m "type(scope): description"
```

### 5. Generate Summary

## Invocation
```bash
gemini /session:end "optional notes"
```

## Expected Output
```
═══════════════════════════════════════
📋 SESSION CLOSED
═══════════════════════════════════════
📅 Date: YYYY-MM-DD

✅ Completed:
   - [list of completed tasks]

📝 Documentation Updated:
   - DEVLOG.md ✓
   - CHANGELOG.md ✓
   - TODO.md ✓

🧪 Tests: PASSED / FAILED
📦 Commit: [commit hash] / SKIPPED

💡 Next Session:
   - [suggested tasks]
═══════════════════════════════════════
```
