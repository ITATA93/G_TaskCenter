Perform a comprehensive team review using Agent Teams (Opus 4.6).

Spin up the following agents in parallel as a coordinated team:

## Agent 1: Code Reviewer (effort: max)
- Execute `git diff HEAD~1` to identify recent changes
- Review for security vulnerabilities, logic errors, and code quality
- Check error handling and edge cases
- Classify findings: 🔴 Critical | 🟡 Medium | 🟢 Low | 💡 Suggestion

## Agent 2: Test Writer (effort: high)
- Analyze the changed files from the diff
- Check if tests exist for modified functions
- Identify untested code paths and missing edge cases
- Generate test stubs for any gaps found

## Agent 3: Doc Writer (effort: medium)
- Check if documentation matches the current code
- Verify CHANGELOG.md is up to date
- Check if DEVLOG.md reflects recent work
- Identify any stale or missing documentation

## Coordination
After all agents complete, synthesize results into a single report:

### Team Review Summary
1. **Code Quality**: [verdict from code-reviewer]
2. **Test Coverage**: [verdict from test-writer]
3. **Documentation**: [verdict from doc-writer]
4. **Overall Verdict**: APPROVED / NEEDS_CHANGES / BLOCKED
5. **Action Items**: Prioritized list of required changes

Additional context from user: {{input}}
