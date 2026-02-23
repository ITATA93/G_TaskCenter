Perform a quick code review of recent changes:

1. Execute `git diff HEAD~1` to see latest changes
2. For each modified file:
   - Check for potential bugs
   - Verify error handling
   - Check for security issues (exposed secrets, injection vulnerabilities)
   - Verify type hints/types are present
   - Check for code duplication
3. Classify findings by severity:
   - 🔴 Critical: Security, data loss, blocking bugs
   - 🟡 Medium: Logic errors, missing error handling
   - 🟢 Low: Code style, minor improvements
   - 💡 Suggestion: Optional enhancements
4. Give verdict: APPROVED / NEEDS_CHANGES / BLOCKED

Be thorough but constructive. Focus on actionable feedback.

Additional context from user: {{input}}
