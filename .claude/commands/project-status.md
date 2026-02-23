Analyze the current project status:

1. Read docs/DEVLOG.md (last entry)
2. Read docs/TODO.md (pending tasks)
3. Execute `git log --oneline -5`
4. Execute `git status`
5. Count lines of code: `find src/ -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) | xargs wc -l 2>/dev/null | tail -1`
6. Count tests: `find tests/ -name "test_*" -o -name "*.test.*" | wc -l`

Present a brief executive summary with:
- Last work completed
- Priority pending tasks
- Git status
- Project metrics
- Suggested next action
