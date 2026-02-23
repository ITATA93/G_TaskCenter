---
description: Common safe operations that can be auto-approved (turbo mode)
---

// turbo-all

# Turbo Operations

This workflow defines safe operations that can be auto-run without manual approval.
The `// turbo-all` annotation above means ALL steps in this workflow auto-run.

When this workflow is referenced (`@turbo-ops`), the agent SHOULD auto-approve
all operations listed below by setting `SafeToAutoRun: true`.

## Safe Read Operations
1. `git status` — Check current state
2. `git log` — View commits
3. `git diff` — View changes
4. `git branch` — List branches
5. `git remote -v` — Show remotes
6. `Get-ChildItem` / `ls` / `dir` — List directory contents
7. `Get-Content` / `cat` / `type` — Read file contents
8. `python -m pytest` / `pytest` — Run tests
9. `npm test` / `npm run lint` / `npx` (read-only) — Run tests/linter
10. `pip list` / `pip show` / `pip --version` — Check packages
11. `node --version` / `python --version` / `git --version` — Check versions
12. `Write-Host` / `echo` — Print output
13. `Get-OdbcDriver` / `Get-PSDrive` — System info queries
14. `code --list-extensions` — VS Code extensions
15. `winget list` — List installed software
16. `docker ps` / `docker images` — Docker read operations
17. `Test-Path` / `Resolve-Path` — Path checks
18. `Select-String` / `findstr` / `grep` — Search in files
19. Any `--version` / `--help` command
20. Variable assignments and Write-Host scripts (diagnostic/audit scripts)

## Safe Write Operations (within project)
21. `git add .` — Stage all changes
22. `Copy-Item` within project directories — Sync files
23. `pip install` — Install Python packages (non-destructive, additive)
24. `npm install` — Install Node packages (non-destructive, additive)
25. `winget install` — Install software via winget
26. `git config` — Configure git settings
27. `New-Item` / `mkdir` — Create directories
28. Creating `.env` from `.env.example` — Copy template files
29. `python -m venv` — Create virtual environments

## Operations That ALWAYS Require Approval
- `git commit` — Review commit message
- `git push` — Verify remote
- `Remove-Item` / `rm` / `del` — Destructive deletions
- Database operations (INSERT/UPDATE/DELETE/DROP) — NEVER auto-approve
- Any command with `--force` or `-f` flags
- `git reset --hard` — Destructive git operations
- File modifications outside current project workspace
- `npm uninstall` / `pip uninstall` — Package removal
