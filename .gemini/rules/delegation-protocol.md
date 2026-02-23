# Delegation Protocol — Sub-agent Management

## When to Delegate

| Task Type | Sub-agent | Trigger Keywords |
|-----------|-----------|------------------|
| Code analysis | code-analyst | analyze, explain, how works, structure |
| Documentation | doc-writer | document, README, CHANGELOG, DEVLOG |
| Code review | code-reviewer | review, audit, bugs, security |
| Testing | test-writer | test, coverage, pytest, jest |
| Database | db-analyst | SQL, query, schema, database |
| Deployment | deployer | deploy, docker, CI/CD, kubernetes |

## Delegation Steps

### 1. Trigger Detection
Identify keywords in user request that match sub-agent specialization.

### 2. Context Preparation
```
- Read relevant docs/ files
- Identify files the sub-agent needs access to
- Define expected output format
- Set clear boundaries (read-only vs write permissions)
```

### 3. Invocation
```bash
gemini -e {agent-name} --yolo --sandbox seatbelt -p "{briefing}"
```

### 4. Verification
- Check output meets requirements
- Validate no unintended changes
- Integrate results if satisfactory

### 5. Retry Protocol
- If unsatisfactory: adjust briefing and retry
- Maximum 2 retries
- If still failing: escalate to user

## Parallel Execution Rules
- Maximum 4 sub-agents in parallel
- Each agent must work on DIFFERENT files
- Use locks for shared resources
- Aggregate results after all complete
