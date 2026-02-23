# Core Rules

> **MANDATORY**: Follow `docs/standards/output_governance.md` for ALL file creation.

## Rule 1: Documentation First
- Read existing documentation before making changes
- Update documentation after completing features
- Never leave undocumented code in production

## Rule 2: Safety First
- NEVER execute destructive database operations without explicit confirmation
- NEVER commit secrets, credentials, or sensitive data
- NEVER push to main/master without review
- Always use parameterized queries to prevent injection

## Rule 3: Test Coverage
- All new code must have corresponding tests
- Minimum 80% coverage target
- Tests must pass before commit

## Rule 4: Code Quality
- Follow project style guide
- Use type hints (Python) or TypeScript
- Write self-documenting code
- Keep functions small and focused

## Rule 5: Git Hygiene
- Atomic commits with descriptive messages
- Format: `type(scope): description`
- Types: feat, fix, docs, refactor, test, chore, style, perf
- Never force push to shared branches

## Rule 6: Delegation Protocol
- Use specialized sub-agents for complex tasks
- Provide clear context in delegation briefings
- Verify sub-agent output before integration
- Maximum 2 retries per delegation
